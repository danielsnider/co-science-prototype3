from coslib.coslib import cos_packages
from coslib.coslib import cos_nodes
import yaml
import os
import click
import glob2
import pprint

@click.group()
def launch():
  """Launch multiple COS nodes."""
  pass # This defines the CLI command group.

pkgs = cos_packages.collect_package_info()


def _launch(launch_file,pkg):
  """Do the real work of launching nodes"""
  # pprint.pprint(launch_file)
  launch_config = yaml.load(file(launch_file, 'r'))
  launch_name = os.path.basename(launch_file)
  nodes = launch_config['nodes']

  print('\nLAUNCH SUMMARY')
  print('===============')
  print('Package: %s' % pkg['name'])
  print('File: %s' % launch_file)
  print('\nPARAMETERS\n')
  for node in nodes:
    if node['params']:
      for param in node['params']:
        for key, value in param.iteritems():
          print(' * /%s: %s' % (key,value))
  print('\nNODES\n')
  for node in nodes:
    print(' - %s (%s/%s)' % (node['name'],node['package'],node['file']))
  print('\n')

  for node in nodes:
    cos_nodes.run(node)


def define_launchable_commands():
  # TODO: MAJOR SECURITY FLAW, exec should not run any pkg_name or launch_file name!
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
    _launch('{launch_file}',{pkg})
      """
        func = func.format(pkg_name=pkg['name'], launch_name=launch_name, launch_file=launch_file, pkg=pkg)
        exec(func)

define_launchable_commands()