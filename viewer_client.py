#!/usr/bin/env python

from __future__ import print_function
import sys
import grpc
import HDF5_pb2
import HDF5_pb2_grpc

import tables

import numpy as np

from matplotlib import pyplot as plt

from addresses import addresses

# USAGE EXAMPLE
# $ python HDF5_client.py im1 im2 

plt.ion()
def display_image(im):
  plt.clf()
  plt.imshow(im)
  plt.show(block=False)
  plt.waitforbuttonpress()


def run(topic, requested_image):
  grpc_options=[('grpc.max_send_message_length', -1),
           ('grpc.max_receive_message_length', -1)]
  channel = grpc.insecure_channel(addresses[topic],options=grpc_options)
  asset_stub = HDF5_pb2_grpc.AssetStub(channel)
  response = asset_stub.Request(HDF5_pb2.AssetIdentifier(id=requested_image))
  h5file = tables.open_file("in-memory-sample.h5", driver="H5FD_CORE",
                                driver_core_image=response.message.decode('base64'),
                                driver_core_backing_store=0)
  im = h5file.root.im.read()
  display_image(im)
  h5file.close()


def display_image_loop():
  topic = sys.argv[1]
  for requested_image in sys.argv[2:]:
    run(topic, requested_image)

if __name__ == '__main__':
  while True:
    display_image_loop()
