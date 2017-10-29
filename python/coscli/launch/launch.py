import time
from threading import Thread
from coslib.coslib import cos_packages
from coslib.coslib import cos_nodes
from coslib.coslib import cos
import yaml
import click
import os

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

@click.group()
def launch():
  """Launch multiple COS nodes."""
  pass # This defines the CLI command group.

def _launch(launch_file,this_package,pkg_info):
  """Do the real work of launching nodes"""
  # pprint.pprint(launch_file)
  launch_config = yaml.load(file(launch_file, 'r'))
  launch_name = os.path.basename(launch_file)
  nodes = launch_config['nodes'] if 'nodes' in launch_config else []
  if nodes == None:
    nodes = []



  # TODO jinja and cli args

  print('\nLAUNCH SUMMARY')
  print('===============')
  print('File: %s' % launch_file)
  # if not nodes:
  #   print('\nNo nodes found in launch file. Exiting')
  #   return
  print('\nPARAMETERS\n')
  for node in nodes:
    node['params'] = node['params'] if 'params' in node else []
    if node['params'] == None:
      node['params'] = []
    if node['params']:
      for param in node['params']:
        for key, value in param.iteritems():
          print(' * /%s: %s' % (key,value))
  print('\nNODES (PACKAGE/FILE)\n')
  for node in nodes:
    print(' - %s (%s/%s)' % (node['name'],node['package'],node['file']))
  print('\n')

  # Pre-check that requested packages can be found
  for node in nodes:
    try:
      pkg = [pkg for pkg in pkg_info if pkg['name'] == node['package']][0]
    except IndexError:
      pkg_paths = cos_packages.get_package_paths()
      click.secho('Package "%s" not found. Does a "cos-package.yaml" exist for this package in the COS search paths? Search paths: "%s"' % (node['package'],pkg_paths), fg='red')
      return

  for node in nodes:
    pkg = [pkg for pkg in pkg_info if pkg['name'] == node['package']][0]
    method_to_store_every_pkg_ver = 'tar'
    if method_to_store_every_pkg_ver == 'tar':
      # print('Collecting package hash...')
      sha = cos_packages.get_package_src_sha(pkg_info=pkg)
      # print('Package hash: %s' % sha)
      pkg['src_sha'] = sha
      # store package info, shar and param info in KV store
      # store package tar in where?

    # Generate mapping from topic to GRPC IP/port
    generate_grpc_mapping(pkg, node)

    thread = Thread(target=cos_nodes.run, args=(pkg, node))
    thread.daemon = True # So that it stops when the parent is stopped
    thread.start()

  ## ACTIONS
  time.sleep(2) # TODO: Wait till everything has started and is ready
  actions = launch_config['actions'] if 'actions' in launch_config else []
  for action in actions:
    cos.init_node('Cos Launch Action Executor')
    topic = action.keys()[0]
    for selector in action[topic]:
      cos.loginfo('Requesting %s on topic %s' % (selector, topic))
      im = cos.request(topic,selector)
  if actions:
    cos.loginfo('Finished executing actions.')

  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    pass

def generate_grpc_mapping(pkg, node):
  pass

def define_launchable_commands():
  # TODO: MAJOR SECURITY FLAW, exec should not run any pkg_name or launch_file name!
  pkgs = cos_packages.collect_package_info()

  for pkg in pkgs:
    func = """
@launch.group()
@click.option('--count', default=1, help='Number of greetings.')
def {pkg_name}(count):
    pass
    """
    func = func.format(pkg_name=pkg['name'])
    exec(func)

    for launch_file in pkg['launch files']:
        launch_name = os.path.basename(launch_file).split('.launch')[0]
        func = """
@{pkg_name}.command()
@click.option('--count', default=1, help='Number of greetings.')
def {launch_name}(count):
    _launch('{launch_file}',{pkg},{pkgs})
      """
        func = func.format(pkg_name=pkg['name'], launch_name=launch_name, launch_file=launch_file, pkg=pkg, pkgs=pkgs)
        exec(func)

define_launchable_commands()