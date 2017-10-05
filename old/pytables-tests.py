#!/usr/bin/env python

import tables
import numpy as np
import glob
import skimage
import skimage.io
import time

from matplotlib import pyplot as plt

plt.ion()
def display_image(im):
  plt.clf()
  plt.imshow(im)
  plt.show(block=False)
  plt.waitforbuttonpress()


for filename in glob.iglob('./images/*'):
  print('%s' % filename)
  im = skimage.io.imread(filename)

  break


h5file = tables.open_file("new_sample.h5", "w", driver="H5FD_CORE", driver_core_backing_store=0)
a = h5file.create_array(h5file.root, "array", np.zeros((300, 300)))
b = h5file.create_array(h5file.root, "im", im)


from IPython import embed
embed() # drop into an IPython session

bim = b.read()
display_image(bim)


h5bytes = h5file.get_file_image()

h5file.close()

