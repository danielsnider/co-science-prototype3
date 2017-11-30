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



def topic_to_rpc_url(topics):
  # TODO: DEFINE IF NOT EXISTS
  # mapping = { # docker
  #   'image': '172.17.0.1:50051',
  #   'image.filter.gaussian': '172.17.0.2:50052',
  #   'image.filter.laplace': '172.17.0.2:50053',
  #   'viewer_trigger': '127.0.0.1:50054'
  # }

  mapping = {
    # 'image': '127.0.0.1:0', # AUTO-SET PORT NUMBER
    'image.row': 'localhost:50051',
    'image.column': 'localhost:50051',
    'image.field': 'localhost:50051',
    'image.plate': 'localhost:50051',
    'image.channel': 'localhost:50051',
    'image.time': 'localhost:50051',
    # 'gaus': 'localhost:50052',
    # 'image.filter.laplace': 'localhost:50053',
    # 'image.filter.gaussian': 'localhost:50052',
    'cc.image.image': 'localhost:50050',
    'cc.image.filename': 'localhost:50050',
    'image.image': 'localhost:50051',
    'image.filename': 'localhost:50051',
    'cc.image.segmentation.watershed': 'localhost:50054',
    'image.segmentation.watershed': 'localhost:50055',
    'viewer_trigger': 'localhost:50056',
    'cell.id': 'localhost:50055',
    'cell.x': 'localhost:50055',
    'cell.y': 'localhost:50055'
  }

  results = {}
  for topic in topics:
    if mapping[topic] not in results:
      results[mapping[topic]]=[]
    results[mapping[topic]].append(topic)

  return results


def topic_to_one_rpc_url(output_topic):
  """ Check that there is only one output url and return it as a string """
  output_url = topic_to_rpc_url(output_topic)
  if len(output_url.keys()) > 1:
    msg = 'Unable to get one output url because there is more than one: %s' % output_url
    logerr(msg)
    raise Exception(msg)
  return output_url.keys()[0] # return url as a string

def hdf5_response_to_data_in(response, fields):
  h5file = tables.open_file("in-memory-sample.h5", driver="H5FD_CORE",
                                  driver_core_image=response.message.decode('base64'),
                                  driver_core_backing_store=0)
  data_in = []
  for field in fields:
    field_name = field.split('image.')[1]
    if field_name in ['image', 'segmentation.watershed']:  # get array type fields
      data_in_part = h5file.root.im.read()
    else:
      data_in_part = h5file.root.im._v_attrs[field_name]
    data_in.append(data_in_part)

  h5file.close()
  return data_in

def get_field_from_hdf5(h5file, field):
  field_name = field.split('image.')[1]
  if field_name in ['image', 'segmentation.watershed']:  # get array type fields
    data_in_part = h5file.root.im.read()
  else:
    data_in_part = h5file.root.im._v_attrs[field_name]
  return data_in_part

def create_grpc_channels(input_urls):
  if type(input_urls) == str: # # needed for cos.request
    input_urls = [input_urls]
  if type(input_urls) == list:
    input_urls={key:'*' for key in input_urls} # needed for cos.request. This will convert a list to dict format like launch files produce in node sections. Eg. ['a'] -> {'a':'*'}
  channel_stubs = {}

  for input_url in input_urls.keys():
    grpc_options=[('grpc.max_send_message_length', -1),
             ('grpc.max_receive_message_length', -1)]
    channel = grpc.insecure_channel(input_url,options=grpc_options)
    channel_stub = HDF5_pb2_grpc.AssetStub(channel)
    channel_stubs[input_url]=channel_stub
  
  return channel_stubs

def spin():
  while True:
    time.sleep(_ONE_DAY_IN_SECONDS)

topics = []
def close():
  global topics
  for topic in topics:
    topic.stop()


###
### REQUEST
###
def request(topic, selector, fields=None, node_name=None):
  try:
    topic_url = topic_to_one_rpc_url(topic) # NOTE: multiple topics not yet supported
    logdebug('requesting on topic %s' % topic)
    channel_stub = create_grpc_channels(topic_url)[topic_url] # NOTE: multiple topics not yet supported
    response = channel_stub.GetAsset(HDF5_pb2.AssetRequest(selector=selector, fields=fields))
    if response.message in ['CosNone', 'CosError']:
      return
    data_in = hdf5_response_to_data_in(response)
    return data_in
  except grpc._channel._Rendezvous as e:
    err_msg = e._state.details.split('Exception calling application: ')[-1]
    logerr('Error in node: %s. Message: "%s"' % (node_name,err_msg))
    if err_msg == 'Connect Failed':
      logerr("Is the rode running? Is it reachable on its assigned address of '%s'?" % topic_url)
    # raise e   # Don't raise a stacktrace here, it wasn't us, it was the other node
  except Exception:
    logerr('Error in node: %s' % node_name)
    raise

###
### NODE (consumer, poducer, or prosumer)
###
class Node(HDF5_pb2_grpc.AssetServicer):
  def __init__(self, params, callback):
    try:
      global topics
      topics.append(self)
      self.node_name = params['node_name']
      logger.name = self.node_name
      self.UserCallback = callback
      self.node_type = params['node_type']
      if not self.node_type == 'producer': # Producers have no input topic
        self.input_topics = params['input_topic']
        self.input_urls = topic_to_rpc_url(self.input_topics)
        self.InputGetters = create_grpc_channels(self.input_urls)
      self.output_topic = params['output_topic']
      self.output_url = topic_to_one_rpc_url(self.output_topic)
      self.num_workers = params['num_workers']
      self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.num_workers))
      pkg_info  = {'src_sha': 'eontue9u409'} # TODO: Get from param server?
      self.output_cache = cos_cache.CacheService(self.node_name, pkg_info)
      self.start()
    except Exception as e:
      logerr('Error in __init__ of this node: %s' % self.node_name)
      self.stop()
      raise e

  def GetAsset(self, request, context):
    try:
      # If consumer, don't check cache, always return None
      if self.node_type == 'consumer':
        # Get data from input topic and do work without creating any result data
        data_in = self.GetDataFromInputTopics(request.selector)
        if not data_in:
          return HDF5_pb2.AssetReply(message='CosError')
        self.UserCallback(*data_in)
        return HDF5_pb2.AssetReply(message='CosNone')

      # If pro* and cache hit, don't do callback
      cached_data = self.output_cache.lookup(request.selector) # TODO: allow returning None as a valid cache hit result
      if cached_data:
        # create new hdf5 and keep only what we need to drop parent information and other possible stuff
        h5single = tables.open_file("new_im.h5", "w", driver="H5FD_CORE",
                                  driver_core_backing_store=0)
        h5single.create_array(h5single.root, 'im', cached_data.read())
        cached_data._v_attrs._f_copy(h5single.root.im) # copy attributes
        data_out_b64 = h5single.get_file_image().encode('base64')
        h5single.close()
        return HDF5_pb2.AssetReply(message=data_out_b64)

      # If cache miss
      if self.node_type == 'producer':
        # Access new data and return it to the requester
        data_out = self.UserCallback(request)
      if self.node_type == 'prosumer':
        # Access data from another node, manipulate it, and return it to the requester
        data_in = self.GetDataFromInputTopics(request.selector)
        data_out = self.UserCallback(*data_in)

      # return data to the requester
      h5single = tables.open_file("new_im.h5", "w", driver="H5FD_CORE",
                                driver_core_backing_store=0)
      if type(data_out).__name__ == 'ndarray': # TODO: fix this
        h5single.create_array(h5single.root, 'im', data_out)
      else: # PyTables node
      # try:
      # except:
      #   from IPython import embed
      #   embed() # drop into an IPython session
        h5single.create_array(h5single.root, 'im', data_out.read())
        data_out._v_attrs._f_copy(h5single.root.im) # copy attributes
      # fields = message.fields  # TODO: only respond with the fields requested
      data_out_b64 = h5single.get_file_image().encode('base64')
      self.output_cache.insert_cache_entry(request.selector, h5single.root.im)
      h5single.close()
      return HDF5_pb2.AssetReply(message=data_out_b64)
    except Exception:
      logerr('GetAsset() Error in this node: %s' % self.node_name)
      raise

  def GetDataFromInputTopics(self, selector):
    # Do GRPC calls to get data from other nodes
    grpc_request = HDF5_pb2.AssetRequest(selector=selector, fields=str(self.input_topics))
    hdf5_responses = {}
    for input_url in self.input_urls.keys():
      try:
        response = self.InputGetters[input_url].GetAsset(grpc_request)
        h5file = tables.open_file("in-memory%s.h5"%input_url, driver="H5FD_CORE",
                                        driver_core_image=response.message.decode('base64'),
                                        driver_core_backing_store=0)
        hdf5_responses[input_url] = h5file
      except grpc._channel._Rendezvous as e:
        in_fields = self.input_urls[input_url]
        err_msg = e._state.details.split('Exception calling application: ')[-1]
        logerr('GetDataFromInputTopics() Error received by this node "%s" from remote node "%s". Message: "%s"' % (self.node_name, input_url,err_msg))
        if err_msg == 'Connect Failed':
          logerr("Trying to reach the data fields '%s'. Is the rode running? Is it reachable on its assigned address of '%s'?" % (in_fields, input_url))
        # raise e   # Don't raise a stacktrace here, it wasn't us, it was the other node
        return

    # Get all fields out of response hdf5 files in the correct order according to self.input_topics
    data_in = []
    for field in self.input_topics:
      url = field_to_url(self.input_urls, field)
      h5file = hdf5_responses[url]
      one_field_from_one_node = get_field_from_hdf5(h5file, field)
      data_in.append(one_field_from_one_node)

    # Cleanup HDF5 files
    for h5file in hdf5_responses.keys():
      hdf5_responses[h5file].close()

    return data_in

  def start(self):
    HDF5_pb2_grpc.add_AssetServicer_to_server(self, self.grpc_server)
    while self.grpc_server.add_insecure_port(self.output_url) == 0:
      logerr('Unable to assign address: %s' % self.output_url)
      time.sleep(2)
    self.grpc_server.start()
    logdebug('output fields ready: %s' % self.output_topic)
    try:
      while True:
        time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
      self.stop()

  def stop(self):
    if hasattr(self, 'cache'):
      self.output_cache.close()
    if hasattr(self, 'grpc_server'):
      self.grpc_server.stop(0) # This exits the process immediately and so must be last

def field_to_url(url_dict, field):
  """ Example Usage
      Input:
        url_dict = {'localhost:50051': ['image.image']}
        field = 'image.image'
      Output:
        'localhost:50051'
  """
  for key, values in url_dict.iteritems():
      for value in values:
        if value == field:
          return key


###
### CONSUMER
###
def consumer(name=None, In=None, cb=None):
  params = {
    'node_name': name,
    'input_topic': In,
    'output_topic': ['%s_trigger' % name],
    'num_workers': 10,
    'node_type':'consumer'
  }
  start_node_thread(params,cb)

###
### PRODUCER
###
def producer(name=None, out=None, cb=None):
  params = {
    'node_name': name,
    'intput_topic': None,
    'output_topic': out,
    'num_workers': 10,
    'node_type':'producer'
  }
  start_node_thread(params,cb)

###
### PROSUMER
###
def prosumer(name=None, In=None, out=None, cb=None):
  params = {
    'node_name': name,
    'input_topic': In,
    'output_topic': out,
    'num_workers': 10,
    'node_type':'prosumer'
  }
  start_node_thread(params,cb)

def start_node_thread(params, cb):
  thread = Thread(target=Node, args=(params, cb))
  thread.daemon = True # So that it stops when the parent is stopped
  thread.start()

