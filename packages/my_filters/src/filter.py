#!/usr/bin/env python
import skimage
import skimage.filters
import tables
from coslib.coslib import cos


def gaussian_filter(im):
  im = skimage.filters.gaussian(im,sigma=4)
  cos.loginfo('done gaussian_filter')
  return im

def laplacian_filter(im):
  im = skimage.filters.laplace(im)
  cos.loginfo('done laplacian_filter')
  return im

if __name__ == '__main__':
  cos.init_node('filter')
  cos.prosumer(In='image', out='image.filter.gaussian', cb=gaussian_filter)
  cos.prosumer(In='image', out='image.filter.laplace', cb=laplacian_filter)
  try:
    cos.spin()
  except KeyboardInterrupt:
    cos.loginfo('exiting filter')
