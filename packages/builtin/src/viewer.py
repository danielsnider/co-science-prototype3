#!/usr/bin/env python

import numpy as np
from coslib.coslib import cos
from matplotlib import pyplot as plt
import matplotlib.patheffects as path_effects


plt.ion()
def display_image(image, filename):
  cos.loginfo('displaying image!')
  plt.clf()
  plt.imshow(image)
  if filename:
    text=plt.text(image.shape[1]/2, image.shape[0]-100, filename, color='white',
                            ha='center', va='center') # position bottom middle
    text.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'),
                         path_effects.Normal()])
  plt.show(block=False)
  plt.waitforbuttonpress()
  plt.close()

if __name__ == '__main__':
  cos.consumer(name='viewer', In=['image.segmentation.watershed', 'image.filename'], cb=display_image)
  try:
    cos.spin()
  except KeyboardInterrupt:
    cos.loginfo('exiting viewer')
    cos.close()
