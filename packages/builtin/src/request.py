#!/usr/bin/env python

from coslib.coslib import cos


if __name__ == '__main__':
  cos.init_node('request')
  im = cos.request('image','im0')
  print(im.__class__)