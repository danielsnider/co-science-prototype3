#!/usr/bin/env python

import numpy as np
from coslib.coslib import cos
from matplotlib import pyplot as plt

plt.ion()
def display_image(image):
  # image['original']
  # image['label']
  cos.loginfo('displaying image!')
  f, axarr = plt.subplots(2)
  axarr[0].imshow(image)
  axarr[0].set_title('Original')
  axarr[1].imshow(image)
  axarr[1].set_title('Labels')
  plt.show(block=False)
  plt.waitforbuttonpress()

# USAGE EXAMPLE
# $ python viewer.py TOPIC IMG_ID
# def request_image():
#   topic = sys.argv[1]
#   requested_image = sys.argv[2]
#   im = cos.cos_request(topic, requested_image)
#   display_image(im)

if __name__ == '__main__':
  cos.init_node('viewer')

  input_map = {
    'images': [{
      'labelled': 'image.segmentation.watershed',
      'original': 'image'
      'date':'image.meta.date',
      'file name':'image.meta.file name',
      'animal name':'image.meta.animal name',
    }],
    'date': 'date'
  }

  cos.consumer(In='image', cb=display_image)
  try:
    cos.spin()
  except KeyboardInterrupt:
    cos.loginfo('exiting viewer')
    plt.close()
    cos.close()

