#!/usr/bin/env python

import skimage
import skimage.io
import glob
import tables
import cos

h5file = tables.open_file("new_sample.h5", "w", driver="H5FD_CORE",
                          driver_core_backing_store=0)

for i, filename in enumerate(glob.iglob('../images/*')):
  im = skimage.io.imread(filename)
  array_name = "im%s" % i # eg. im1, im2, etc.
  h5file.create_array(h5file.root, array_name, im)
  print('loaded image %s' % filename)

def get_resource_callback(request):
  return eval('h5file.root.%s' % request.name)

if __name__ == '__main__':
  cos.init_node('reader')
  cos.provide_resource(output_topic='image', callback=get_resource_callback)
