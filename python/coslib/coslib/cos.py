#!/usr/bin/env python

from multiprocessing import Process
from threading import Thread
from concurrent import futures
import time
import grpc
import HDF5_pb2
import HDF5_pb2_grpc
import tables
from coslib.coslib.cos_logging import logger, logdebug, loginfo, logwarn, logerr, logcritical

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
    'image': '127.0.0.1:50051',
    'image.filter.gaussian': '127.0.0.1:50052',
    'gaus': '127.0.0.1:50052',
    'image.filter.laplace': '127.0.0.1:50053',
    'viewer_trigger': '127.0.0.1:50054'
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
  grpc_options=[('grpc.max_send_message_length', -1),
           ('grpc.max_receive_message_length', -1)]
  print('a')
  print('requesting on topic %s' % topic_to_rpc_url(topic))
  channel = grpc.insecure_channel(topic_to_rpc_url(topic),options=grpc_options)
  print('b')
  asset_stub = HDF5_pb2_grpc.AssetStub(channel)
  print('c')
  response = asset_stub.SayAsset(HDF5_pb2.AssetRequest(name=selector))
  print('d')
  h5file = tables.open_file("in-memory-sample.h5", driver="H5FD_CORE",
                                driver_core_image=response.message.decode('base64'),
                                driver_core_backing_store=0)
  im = h5file.root.im.read()
  h5file.close()
  return im

###
### PRODUCER
###
class Producer(HDF5_pb2_grpc.AssetServicer):
  def __init__(self, params, callback):
    self.output_topic = params['output_topic']
    self.output_url = topic_to_rpc_url(self.output_topic)
    self.num_workers = params['num_workers']
    self.callback = callback
    self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.num_workers))
    self.start()

  def SayAsset(self, request, context):
    loginfo("Received request.")
    im = self.callback(request)
    h5single = tables.open_file("new_im.h5", "w", driver="H5FD_CORE",
                              driver_core_backing_store=0)
    h5single.create_array(h5single.root, 'im', im.read())
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
  thread = Process(target=Producer, args=(params, cb))
  thread.daemon = True # So that it stops when the parent is stopped
  try:
    thread.start()
  except KeyboardInterrupt:
    pass





###
### PROSUMER
###
class Prosumer(HDF5_pb2_grpc.AssetServicer):
  def __init__(self, params, callback):
    self.callback = callback
    self.input_topic = params['input_topic']
    self.output_topic = params['output_topic']
    self.input_url = topic_to_rpc_url(self.input_topic)
    self.output_url = topic_to_rpc_url(self.output_topic)
    self.num_workers = params['num_workers']

    self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.num_workers))

    grpc_options=[('grpc.max_send_message_length', -1),
             ('grpc.max_receive_message_length', -1)]
    channel = grpc.insecure_channel(self.input_url,options=grpc_options)
    self.InputGetter = HDF5_pb2_grpc.AssetStub(channel)

    self.start()

  def SayAsset(self, request, context):
    print('1')
    im = self.GetInput(request.name)
    im = self.callback(im) # do user defined work
    h5single = tables.open_file("new_im.h5", "w", driver="H5FD_CORE",
                              driver_core_backing_store=0)
    h5single.create_array(h5single.root, 'im', im)
    data = h5single.get_file_image().encode('base64')
    h5single.close()
    print('3')
    return HDF5_pb2.AssetReply(message=data)

  def GetInput(self, selector):
    print('2')
    req = HDF5_pb2.AssetRequest(name=selector)
    print('2.1')
    response = self.InputGetter.SayAsset(req)
    print('2.2')
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
  thread = Process(target=Prosumer, args=(params, cb))
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
  thread = Thread(target=Prosumer, args=(params, cb))
  thread.daemon = True # So that it stops when the parent is stopped
  try:
    thread.start()
  except KeyboardInterrupt:
    pass

