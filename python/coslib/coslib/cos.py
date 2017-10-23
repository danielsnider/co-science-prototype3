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


def spin():
  while True:
    time.sleep(_ONE_DAY_IN_SECONDS)

# TODO: Class instead ofthis node_name global variable 
node_name = None # used in trigger topic name
def init_node(name):
  logger.name = name
  global node_name
  node_name = name

###
### REQUEST
###
def request(topic, selector):
  try:
    grpc_options=[('grpc.max_send_message_length', -1),
             ('grpc.max_receive_message_length', -1)]
    logdebug('requesting on topic %s' % topic_to_rpc_url(topic))
    channel = grpc.insecure_channel(topic_to_rpc_url(topic),options=grpc_options)
    asset_stub = HDF5_pb2_grpc.AssetStub(channel)
    response = asset_stub.GetAsset(HDF5_pb2.AssetRequest(selector=selector))
    if response.message == 'None':
      return
    h5file = tables.open_file("in-memory-sample.h5", driver="H5FD_CORE",
                                  driver_core_image=response.message.decode('base64'),
                                  driver_core_backing_store=0)
    im = h5file.root.im.read()
    h5file.close()
    return im
  except Exception as e:
    global node_name
    logerr('Error in node: %s' % node_name)
    raise e

###
### PRODUCER
###
class Producer(HDF5_pb2_grpc.AssetServicer):
  def __init__(self, params, callback):
    try:
      self.output_topic = params['output_topic']
      self.output_url = topic_to_rpc_url(self.output_topic)
      self.num_workers = params['num_workers']
      self.callback = callback
      self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.num_workers))
      global node_name
      pkg_info  = {'src_sha': 'eontue9u409'} # TODO: Get from param server?
      self.cache = cos_cache.CacheService(node_name, pkg_info)
      self.start()
    except Exception as e:
      global node_name
      logerr('Error in node: %s' % node_name)
      raise e

  def GetAsset(self, request, context):
    im = self.cache.lookup(request.selector)
    if im:
      logdebug("cache hit")
    if not im:
      logdebug("cache miss")
      im = self.callback(request)
      if im.__class__ is tables.array.Array:
        im = im.read()
      self.cache.insert_cache_entry(request.selector, im)
    h5single = tables.open_file("new_im.h5", "w", driver="H5FD_CORE",
                              driver_core_backing_store=0)
    if im.__class__ is tables.array.Array:
      im = im.read()
    h5single.create_array(h5single.root, 'im', im)
    data = h5single.get_file_image().encode('base64')
    h5single.close()
    return HDF5_pb2.AssetReply(message=data)

  def start(self):
    HDF5_pb2_grpc.add_AssetServicer_to_server(self, self.grpc_server)
    while self.grpc_server.add_insecure_port(self.output_url) == 0:
      logerr('Unable to assign address: %s' % self.output_url)
      time.sleep(2)
    self.grpc_server.start()
    logdebug('output topic ready: %s' % self.output_topic)
    try:
      # TODO: check for new params? PUSH would be better than polling
      while True:
        time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
      self.grpc_server.stop(0) # This exits the process immediately and so must be last

def producer(out=None, cb=None):
  params = {
    'output_topic': out,
    'num_workers': 10
  }
  thread = Thread(target=Producer, args=(params, cb))
  thread.daemon = True # So that it stops when the parent is stopped
  try:
    thread.start()
  except KeyboardInterrupt:
    pass
  except Exception as e:
    global node_name
    logerr('Error in node: %s' % node_name)
    raise e





###
### PROSUMER
###
class Prosumer(HDF5_pb2_grpc.AssetServicer):
  def __init__(self, params, callback, consumer_only):
    try:
      self.callback = callback
      self.consumer_only = consumer_only
      self.input_topic = params['input_topic']
      self.output_topic = params['output_topic']
      self.input_url = topic_to_rpc_url(self.input_topic)
      self.output_url = topic_to_rpc_url(self.output_topic)
      self.num_workers = params['num_workers']
      self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.num_workers))
      global node_name
      pkg_info  = {'src_sha': 'eontue9u409'} # TODO: Get from param server?
      self.cache = cos_cache.CacheService(node_name, pkg_info)
      grpc_options=[('grpc.max_send_message_length', -1),
               ('grpc.max_receive_message_length', -1)]
      channel = grpc.insecure_channel(self.input_url,options=grpc_options)
      self.InputGetter = HDF5_pb2_grpc.AssetStub(channel)
      self.start()
    except Exception as e:
      global node_name
      logerr('Error in node: %s' % node_name)
      raise e


  def GetAsset(self, request, context):
    if self.consumer_only:
        im = self.GetInput(request.selector)
        self.callback(im)
        return HDF5_pb2.AssetReply(message='None')
    # PROSUMER SECTION (TODO: this is probably better as a seperate class)
    im = self.cache.lookup(request.selector) # TODO: allow returning None as a valid cache hit result
    if im:
      logdebug("cache hit")
    if not im:
      im = self.GetInput(request.selector)
      logdebug("cache miss")
      im = self.callback(im)
      self.cache.insert_cache_entry(request.selector, im)
    h5single = tables.open_file("new_im.h5", "w", driver="H5FD_CORE",
                              driver_core_backing_store=0)
    if im.__class__ is tables.array.Array:
      im = im.read()
    h5single.create_array(h5single.root, 'im', im)
    data = h5single.get_file_image().encode('base64')
    h5single.close()
    return HDF5_pb2.AssetReply(message=data)

  def GetInput(self, selector):
    req = HDF5_pb2.AssetRequest(selector=selector)
    response = self.InputGetter.GetAsset(req)
    h5file = tables.open_file("in-memory-sample.h5", driver="H5FD_CORE",
                                  driver_core_image=response.message.decode('base64'),
                                  driver_core_backing_store=0)
    im = h5file.root.im.read()
    h5file.close()
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
    self.grpc_server.stop(0) # This exits the process immediately and so must be last

def prosumer(In=None, out=None, cb=None):
  params = {
    'input_topic': In,
    'output_topic': out,
    'num_workers': 10
  }
  consumer_only=False
  thread = Thread(target=Prosumer, args=(params, cb, consumer_only))
  thread.daemon = True # So that it stops when the parent is stopped
  try:
    thread.start()
  except KeyboardInterrupt:
    pass




###
### CONSUMER
###
def consumer(In=None, cb=None):
  params = {
    'input_topic': In,
    'output_topic': '%s_trigger' % node_name,
    'num_workers': 10
  }
  consumer_only=True
  thread = Thread(target=Prosumer, args=(params, cb, consumer_only))
  thread.daemon = True # So that it stops when the parent is stopped
  try:
    thread.start()
  except KeyboardInterrupt:
    pass

