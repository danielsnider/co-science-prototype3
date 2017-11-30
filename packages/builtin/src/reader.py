#!/usr/bin/env python

import os
import skimage
import skimage.io
import glob
import tables
from coslib.coslib import cos
import re

h5file = tables.open_file("new_sample.h5", "w", driver="H5FD_CORE",
                          driver_core_backing_store=0)

i = 0
for filename in glob.iglob('../images/*'):
  # Load
  if os.path.isdir(filename):
    continue
  im = skimage.io.imread(filename)

  # Create hdf5
  array_name = "im%s" % i # eg. im1, im2, etc.
  arr = h5file.create_array(h5file.root, array_name, im)

  # Add metadata
  name = 'r02c02f06p01-ch3sk74fk1fl1.tif'
  exp = re.compile('r(?P<row>\d+)c(?P<column>\d+)f(?P<field>\d+)p(?P<plate>\d+)-ch(?P<channel>\d+)sk(?P<time>\d+)')
  r=exp.search(name)
  filename_dict = r.groupdict()
  for key, value in filename_dict.iteritems():
    arr._f_setattr(key,value)
  arr._f_setattr('filename',filename)
  
  cos.loginfo('loaded image %s to array_name "%s"' % (filename, array_name))
  i+=1

def get_resource_callback(request):
  try:
    H5_node = eval('h5file.root.%s' % request.selector[0])
    image = H5_node.read()
    row = H5_node._v_attrs['row']
    column = H5_node._v_attrs['column']
    field = H5_node._v_attrs['field']
    plate = H5_node._v_attrs['plate']
    channel = H5_node._v_attrs['channel']
    time = H5_node._v_attrs['time']
    filename = H5_node._v_attrs['filename']
    return image, row, column, field, plate, channel, time, filename

  except tables.exceptions.NoSuchNodeError as e:
    err_msg = 'Could not find image with id "%s"' % request.selector
    cos.logerr(err_msg)
    cos.logerr('I have available\n%s' % h5file.list_nodes('/'))
    raise Exception(err_msg)

if __name__ == '__main__':
  cos.producer(
    name='reader',
    out=[
      'image.image',
      'image.row',
      'image.column',
      'image.field',
      'image.plate',
      'image.channel',
      'image.time',
      'image.filename'],
    cb=get_resource_callback
  )
  try:
    cos.spin()
  except KeyboardInterrupt:
    cos.loginfo('exiting reader')
    h5file.close()
    cos.close()

