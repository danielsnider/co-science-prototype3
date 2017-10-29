#!/usr/bin/env python

# import sys
# sys.path.append('/home/dan/co-science-prototype3/python')
import os
import skimage
import skimage.io
import glob
import tables
from coslib.coslib import cos

h5file = tables.open_file("new_sample.h5", "w", driver="H5FD_CORE",
                          driver_core_backing_store=0)

i = 0
for filename in glob.iglob('../images/*'):
  if os.path.isdir(filename):
    continue
  im = skimage.io.imread(filename)
  array_name = "im%s" % i # eg. im1, im2, etc.
  h5file.create_array(h5file.root, array_name, im)
  cos.loginfo('loaded image %s to array_name "%s"' % (filename, array_name))
  i+=1

def get_resource_callback(request):
  try:
    im = eval('h5file.root.%s' % request.selector)
    return im.read()
  except tables.exceptions.NoSuchNodeError as e:
    err_msg = 'Could not find image with id "%s"' % request.selector
    cos.logerr(err_msg)
    cos.logerr('I have available\n%s' % h5file.list_nodes('/'))
    raise Exception(err_msg)

if __name__ == '__main__':
  cos.init_node('reader')
  cos.producer(out='image', cb=get_resource_callback)
  try:
    cos.spin()
  except KeyboardInterrupt:
    cos.loginfo('exiting reader')
    h5file.close()
    cos.close()

