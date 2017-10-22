#!/usr/bin/env python

import sys
sys.path.append('/home/dan/co-science-prototype3/python')
from coslib.coslib import cos


if __name__ == '__main__':
  cos.init_node('request')
  im = cos.request('viewer_trigger','im0')
  print(im.__class__)