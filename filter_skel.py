#!/usr/bin/env python

import skimage
import skimage.filters
import tables
import cos


def filter_callback(im):
  im = skimage.filters.gaussian(im,sigma=4)
  return im

if __name__ == '__main__':
  cos.init_node('filter')
  cos.create_service(input_topic='image', output_topic='image.filter', callback=filter_callback)

