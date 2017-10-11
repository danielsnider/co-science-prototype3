#!/usr/bin/env python

from threading import Thread

from concurrent import futures
import time

import grpc

import HDF5_pb2
import HDF5_pb2_grpc
import skimage
import skimage.filters
import glob

import tables
from addresses import addresses


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class CosService(HDF5_pb2_grpc.AssetServicer):
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

  # def ProduceOutput(self, request, context):
  def SayAsset(self, request, context):
    im = self.GetInput(request.name)
    im = self.callback(im) # do user defined work
    h5single = tables.open_file("new_im.h5", "w", driver="H5FD_CORE",
                              driver_core_backing_store=0)
    h5single.create_array(h5single.root, 'im', im)
    data = h5single.get_file_image().encode('base64')
    h5single.close()
    return HDF5_pb2.AssetReply(message=data)

  def GetInput(self, id):
    response = self.InputGetter.SayAsset(HDF5_pb2.AssetRequest(name=id))
    h5file = tables.open_file("in-memory-sample.h5", driver="H5FD_CORE",
                                  driver_core_image=response.message.decode('base64'),
                                  driver_core_backing_store=0)
    im = h5file.root.im.read()
    h5file.close()
    return im

  def start(self):
    HDF5_pb2_grpc.add_AssetServicer_to_server(self, self.grpc_server)

    self.grpc_server.add_insecure_port(self.output_url)
    self.grpc_server.start()
    print('ready to produce %s' % self.output_topic)
    try:
      while True:
        time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
      self.grpc_server.stop(0)



def topic_to_rpc_url(topic):
  # TODO: DEFINE IF NOT EXISTS
  mapping = {
    'image': 'localhost:50051',
    'image.filter.gaussian': 'localhost:50052',
    'image.filter.laplace': 'localhost:50053'
  }
  return mapping[topic]


def create_service(input_topic, output_topic, callback):
  if not callback:
    print('error')
    return

  params = {
    'input_topic': input_topic,
    'output_topic': output_topic,
    'num_workers': 10 
  }

  thread = Thread(target = CosService, args = (params, callback))
  # thread.daemon = True # So that it stops when the parent is stopped
  thread.start()
  # try:
  #   while True:
  #     time.sleep(_ONE_DAY_IN_SECONDS)
  # except KeyboardInterrupt:
  #   self.grpc_server.stop(0)


def init_node(name):
  print('init node %s' % name)