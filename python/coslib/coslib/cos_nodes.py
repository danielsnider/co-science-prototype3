from coslib.coslib import cos_packages
import pprint
import os
import requests

def run(node_config):
  pkg_info = cos_packages.get_package_info(node_config['package'])
  node_file =  [n for n in pkg_info['nodes'] if node_config['file'] in n][0]

  if '.py' in node_file:
    node_type = 'python'
  
  # check available ports
  #   curl http://localhost:8500/v1/catalog/node/laptop

  # create consul service
  # set parametrs on kv store
  # run launch command
