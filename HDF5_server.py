
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


filename = glob.iglob('./images/*').next() # get first file in directory
im = skimage.io.imread(filename)
h5file = tables.open_file("new_sample.h5", "w", driver="H5FD_CORE",
                          driver_core_backing_store=0)
h5file.create_array(h5file.root, "im", im)

class Greeter(HDF5_pb2_grpc.GreeterServicer):

  def SayHello(self, request, context):
    # from IPython import embed
    # embed() # drop into an IPython session
    # return HDF5_pb2.HelloReply(message='Hello, %s!' % request.name)
    return HDF5_pb2.HelloReply(message=h5file.get_file_image().encode('base64'))


def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  HDF5_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
  server.add_insecure_port('[::]:50051')
  server.start()
  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    server.stop(0)

if __name__ == '__main__':
  serve()
