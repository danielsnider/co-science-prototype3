from __future__ import print_function

import grpc
import HDF5_pb2
import HDF5_pb2_grpc

import tables

import numpy as np

from matplotlib import pyplot as plt

plt.ion()
def display_image(im):
  plt.clf()
  plt.imshow(im)
  plt.show(block=False)
  plt.waitforbuttonpress()


def run():
  channel = grpc.insecure_channel('localhost:50051')
  stub = HDF5_pb2_grpc.GreeterStub(channel)
  response = stub.SayHello(HDF5_pb2.HelloRequest(name='you'))
  h5file = tables.open_file("in-memory-sample.h5", driver="H5FD_CORE",
                                driver_core_image=response.message.decode('base64'),
                                driver_core_backing_store=0)
  im = h5file.root.im.read()
  display_image(im)
  h5file.close()




if __name__ == '__main__':
  run()
