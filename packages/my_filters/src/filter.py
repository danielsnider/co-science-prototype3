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
  cos.loginfo('starting filter node')
  cos.init_node('filter')
  cos.create_service(input_topic='image', output_topic='image.filter.gaussian', callback=gaussian_filter)
  cos.create_service(input_topic='image', output_topic='image.filter.laplace', callback=laplacian_filter)

