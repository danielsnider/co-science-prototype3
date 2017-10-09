#!/usr/bin/env python

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


### SERVER
class Asset(HDF5_pb2_grpc.AssetServicer):

  def Request(self, request, context):
    im = get_image(request.id)
    im2 = skimage.filters.gaussian(im,sigma=4)
    h5single = tables.open_file("new_im.h5", "w", driver="H5FD_CORE",
                              driver_core_backing_store=0)
    h5single.create_array(h5single.root, 'im', im2)
    data = h5single.get_file_image().encode('base64')
    h5single.close()
    return HDF5_pb2.HDF5Reply(message=data)

def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  HDF5_pb2_grpc.add_AssetServicer_to_server(Asset(), server)
  server.add_insecure_port(addresses['filterA'])
  server.start()
  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    server.stop(0)
    h5file.close()


### CLIENT
def get_image(requested_image):
  grpc_options=[('grpc.max_send_message_length', -1),
           ('grpc.max_receive_message_length', -1)]
  channel = grpc.insecure_channel(addresses['reader'],options=grpc_options)
  asset_stub = HDF5_pb2_grpc.AssetStub(channel)
  response = asset_stub.Request(HDF5_pb2.AssetIdentifier(id=requested_image))
  h5file = tables.open_file("in-memory-sample.h5", driver="H5FD_CORE",
                                driver_core_image=response.message.decode('base64'),
                                driver_core_backing_store=0)
  im = h5file.root.im.read()
  # display_image(im)
  h5file.close()
  return im

if __name__ == '__main__':
  serve()
