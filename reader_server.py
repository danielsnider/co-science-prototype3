#!/usr/bin/env python

from concurrent import futures
import time

import grpc

import HDF5_pb2
import HDF5_pb2_grpc
import skimage
import skimage.io
import glob

import tables

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


h5file = tables.open_file("new_sample.h5", "w", driver="H5FD_CORE",
                          driver_core_backing_store=0)

for i, filename in enumerate(glob.iglob('./images/*')):
  im = skimage.io.imread(filename)
  array_name = "im%s" % i # eg. im1, im2, etc.
  h5file.create_array(h5file.root, array_name, im)
  print('loaded image %s' % filename)

class Asset(HDF5_pb2_grpc.AssetServicer):

  def Request(self, request, context):
    im = eval('h5file.root.%s' % request.id)
    h5single = tables.open_file("new_im.h5", "w", driver="H5FD_CORE",
                              driver_core_backing_store=0)
    h5single.create_array(h5single.root, 'im', im.read())
    data = h5single.get_file_image().encode('base64')
    h5single.close()
    return HDF5_pb2.HDF5Reply(message=data)


def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  HDF5_pb2_grpc.add_AssetServicer_to_server(Asset(), server)
  server.add_insecure_port('[::]:50051')
  server.start()
  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    server.stop(0)
    h5file.close()


if __name__ == '__main__':
  serve()
