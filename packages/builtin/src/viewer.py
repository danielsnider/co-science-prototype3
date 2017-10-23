#!/usr/bin/env python

# import sys
# sys.path.append('/home/dan/co-science-prototype3/python')
import tables
import numpy as np
from coslib.coslib import cos
from matplotlib import pyplot as plt

plt.ion()
def display_image(im):
  cos.loginfo('displaying image!')
  plt.clf()
  plt.imshow(im)
  plt.show(block=False)
  plt.waitforbuttonpress()
  plt.close()

# USAGE EXAMPLE
# $ python viewer.py TOPIC IMG_ID
# def request_image():
#   topic = sys.argv[1]
#   requested_image = sys.argv[2]
#   im = cos.cos_request(topic, requested_image)
#   display_image(im)

if __name__ == '__main__':
  cos.init_node('viewer')
  cos.consumer(In='image.filter.gaussian', cb=display_image)
  try:
    cos.spin()
  except KeyboardInterrupt:
    cos.loginfo('exiting viewer')
