#!/usr/bin/env python

from concurrent import futures
import grpc
import HDF5_pb2
import HDF5_pb2_grpc


from threading import Thread
import time
import tables
from coslib.coslib.cos_logging import logger, logdebug, loginfo, logwarn, logerr, logcritical

from coslib.coslib import cos_cache

_ONE_DAY_IN_SECONDS = 60 * 60 * 24



# TODO: Class instead ofthis node_name global variable 
node_name = None # used in trigger topic name
def init_node(name):
  logger.name = name
  global node_name
  node_name = name


def topic_to_rpc_url(topic):
  # TODO: DEFINE IF NOT EXISTS
  # mapping = { # docker
  #   'image': '172.17.0.1:50051',
  #   'image.filter.gaussian': '172.17.0.2:50052',
  #   'image.filter.laplace': '172.17.0.2:50053',
  #   'viewer_trigger': '127.0.0.1:50054'
  # }
  mapping = {
    # 'image': '127.0.0.1:0', # AUTO-SET PORT NUMBER
    'image': 'localhost:50051',
    'image.filter.gaussian': 'localhost:50052',
    'gaus': 'localhost:50052',
    'image.filter.laplace': 'localhost:50053',
    'viewer_trigger': 'localhost:50054'
  }
  return mapping[topic]

def hdf5_response_to_im(response):
  h5file = tables.open_file("in-memory-sample.h5", driver="H5FD_CORE",
                                  driver_core_image=response.message.decode('base64'),
                                  driver_core_backing_store=0)
  im = h5file.root.im.read()
  h5file.close()
  return im

def create_grpc_channel_at(input_url):
  grpc_options=[('grpc.max_send_message_length', -1),
           ('grpc.max_receive_message_length', -1)]
  channel = grpc.insecure_channel(input_url,options=grpc_options)
  channel_stub = HDF5_pb2_grpc.AssetStub(channel)
  return channel_stub

def spin():
  while True:
    time.sleep(_ONE_DAY_IN_SECONDS)

###
### REQUEST
###
def request(topic, selector):
  try:
    topic_url = topic_to_rpc_url(topic)
    logdebug('requesting on topic %s' % topic_url)
    channel_stub = create_grpc_channel_at(topic_url)
    response = channel_stub.GetAsset(HDF5_pb2.AssetRequest(selector=selector))
    if response.message == 'None':
      return
    im = hdf5_response_to_im(response)
    return im
  except grpc._channel._Rendezvous as e:
    global node_name
    err_msg = e._state.details.split('Exception calling application: ')[-1]
    logerr('Error in node: %s. Message: "%s"' % (node_name,err_msg))
    if err_msg == 'Connect Failed':
      logerr("Is the rode running and reachable on its assigned address of %s?" % topic_url)
    # raise e   # Don't raise a stacktrace here, it wasn't us, it was the other node
  except Exception as e:
    global node_name
    logerr('Error in node: %s' % node_name)
    raise e

###
### NODE (consumer, poducer, or prosumer)
###
class Node(HDF5_pb2_grpc.AssetServicer):
  def __init__(self, params, callback):
    try:
      global node_name
      self.DoUserCallback = callback
      self.node_type = params['node_type']
      if not self.node_type == 'producer': # Producers have no input topic
        self.input_topic = params['input_topic']
        self.input_url = topic_to_rpc_url(self.input_topic)
        self.InputGetter = create_grpc_channel_at(self.input_url)
      self.output_topic = params['output_topic']
      self.output_url = topic_to_rpc_url(self.output_topic)
      self.num_workers = params['num_workers']
      self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.num_workers))
      pkg_info  = {'src_sha': 'eontue9u409'} # TODO: Get from param server?
      self.cache = cos_cache.CacheService(node_name, pkg_info)
      self.start()
    except Exception as e:
      logerr('Error in node: %s' % node_name)
      raise e

  def GetAsset(self, request, context):
    if self.node_type == 'consumer':
      # Get data from input topic and do work without creating any result data
      im = self.GetDataFromInputTopic(request.selector)
      self.DoUserCallback(im)
      return HDF5_pb2.AssetReply(message='None')
    data = self.cache.lookup(request.selector) # TODO: allow returning None as a valid cache hit result
    if data:
      h5single = tables.open_file("new_im.h5", "w", driver="H5FD_CORE",
                                driver_core_backing_store=0)
      h5single.create_array(h5single.root, 'im', data.read())
      data = h5single.get_file_image().encode('base64')
      h5single.close()
      return HDF5_pb2.AssetReply(message=data)
    else:
      logdebug("[CACHE] miss for request %s" % request)
    if self.node_type == 'producer':
      # Access new data and return it to the requester
      im = self.DoUserCallback(request)
    if self.node_type == 'prosumer':
      # Access data from another node, manipulate it, and return it to the requester
      im = self.GetDataFromInputTopic(request.selector)
      im = self.DoUserCallback(im)
    # return data to the requester
    h5single = tables.open_file("new_im.h5", "w", driver="H5FD_CORE",
                              driver_core_backing_store=0)
    h5single.create_array(h5single.root, 'im', im)
    data = h5single.get_file_image().encode('base64')
    h5single.close()
    self.cache.insert_cache_entry(request.selector, data)
    return HDF5_pb2.AssetReply(message=data)

  def GetDataFromInputTopic(self, selector):
    request = HDF5_pb2.AssetRequest(selector=selector)
    response = self.InputGetter.GetAsset(request)
    im = hdf5_response_to_im(response)
    return im

  def start(self):
    HDF5_pb2_grpc.add_AssetServicer_to_server(self, self.grpc_server)
    while self.grpc_server.add_insecure_port(self.output_url) == 0:
      logerr('Unable to assign address: %s' % self.output_url)
      time.sleep(2)
    self.grpc_server.start()
    logdebug('output topic ready: %s' % self.output_topic)
    try:
      while True:
        time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
      self.stop()

  def stop(self):
    self.cache.close()
    self.grpc_server.stop(0) # This exits the process immediately and so must be last


###
### CONSUMER
###
def consumer(In=None, cb=None):
  params = {
    'input_topic': In,
    'output_topic': '%s_trigger' % node_name,
    'num_workers': 10,
    'node_type':'consumer'
  }
  start_node_thread(params,cb)

###
### PRODUCER
###
def producer(out=None, cb=None):
  params = {
    'intput_topic': None,
    'output_topic': out,
    'num_workers': 10,
    'node_type':'producer'
  }
  start_node_thread(params,cb)

###
### PROSUMER
###
def prosumer(In=None, out=None, cb=None):
  params = {
    'input_topic': In,
    'output_topic': out,
    'num_workers': 10,
    'node_type':'prosumer'
  }
  start_node_thread(params,cb)

def start_node_thread(params, cb):
  thread = Thread(target=Node, args=(params, cb))
  thread.daemon = True # So that it stops when the parent is stopped
  try:
    thread.start()
  except KeyboardInterrupt:
    pass

