from coslib.coslib import cos_packages
import pprint
import os
import requests


import subprocess
# from subprocess import Popen, PIPE
# p = Popen(cmd, stdout=PIPE, stderr=PIPE)
# stdout, stderr = p.communicate()


def run(pkg_info, node_config):
  node_file =  [n for n in pkg_info['nodes'] if node_config['file'] in n][0]

  if '.py' in node_file:
    node_type = 'python'

  print(node_file)

  # p = subprocess.Popen(["the", "command"])
  # p.wait()
  
  # check available ports
  #   curl http://localhost:8500/v1/catalog/node/laptop

  # create consul service
  # set parametrs on kv store
  # run launch command
