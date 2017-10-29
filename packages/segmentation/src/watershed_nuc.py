#!/usr/bin/env python

import numpy as np
import pylab
import mahotas as mh
from coslib.coslib import cos

def segment_nuc(im):
  T = mh.thresholding.otsu(im) # calculate a threshold value

  # apply a gaussian filter that smoothen the image
  smoothed = mh.gaussian_filter(im, 8)
  thresholded= smoothed > T # do threshold

  # Watershed
  smoothed = mh.gaussian_filter(im, 10)
  regional_max = mh.regmax(smoothed)
  dist_im = mh.distance(thresholded)
  seeds,count = mh.label(regional_max) # nuclei count
  watershedded = mh.cwatershed(dist_im, seeds)

  # Remove areas that aren't nuclei
  watershedded[np.logical_not(thresholded)] = 0

  return watershedded

if __name__ == '__main__':
  cos.init_node('watershed')
  cos.prosumer(In='image', out='image.segmentation.watershed', cb=segment_nuc)
  try:
    cos.spin()
  except KeyboardInterrupt:
    cos.loginfo('exiting watershed')
    cos.close()

