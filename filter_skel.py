#!/usr/bin/env python

import skimage
import skimage.filters
import tables
import cos


def filterA(im):
  im = skimage.filters.gaussian(im,sigma=4)
  return im

if __name__ == '__main__':
  cos.define_service(input='image', output='image.filtered', callback=filterA)

