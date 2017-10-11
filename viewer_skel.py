#!/usr/bin/env python

import sys
import tables
import numpy as np
import cos

from matplotlib import pyplot as plt
from addresses import addresses

# USAGE EXAMPLE
# $ python viewer.py TOPIC IMG_ID

plt.ion()
def display_image(im):
  plt.clf()
  plt.imshow(im)
  plt.show(block=False)
  plt.waitforbuttonpress()

def request_image():
  topic = sys.argv[1]
  requested_image = sys.argv[2]
  im = cos.service_request(topic, requested_image)
  display_image(im)

if __name__ == '__main__':
  request_image()
