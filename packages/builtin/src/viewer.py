#!/usr/bin/env python

import numpy as np
from coslib.coslib import cos
from matplotlib import pyplot as plt
import matplotlib.patheffects as path_effects


plt.ion()
def display_image(im):
  cos.loginfo('displaying image!')
  plt.clf()
  plt.imshow(im)
  if im._v_attrs.__contains__('filename'):
    filename=im._v_attrs.filename
    text=plt.text(im.shape[1]/2, im.shape[0]-100, filename, color='white',
                            ha='center', va='center') # position bottom middle
    text.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'),
                         path_effects.Normal()])
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
  cos.consumer(In='image', cb=display_image)
  try:
    cos.spin()
  except KeyboardInterrupt:
    cos.loginfo('exiting viewer')
    cos.close()
