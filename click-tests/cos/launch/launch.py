from cos_python.coslib import cos_packages
import yaml
import os
import click
import glob2

@click.group()
def launch():
    pass

pkgs = cos_packages.collect_package_info()


def _launch(node,pkg):
  print('launching node %s from package %s' %(node,pkg))

# TODO: MAJOR SECURITY FLAW, exec should not run any pkg_name or launch_file name!
for pkg in pkgs:
  func = """@launch.group()
@click.option('--count', default=1, help='Number of greetings.')
def {pkg_name}(count):
    pass
  """
  func = func.format(pkg_name=pkg['name'])
  exec(func)

  launch_files = [os.path.basename(launch_file).split('.launch')[0] for launch_file in pkg['launch files']]
  for launch_file in launch_files:
      func = """@{pkg_name}.command()
@click.option('--count', default=1, help='Number of greetings.')
def {launch_file}(count):
    launch_file = '{launch_file}'
    pkg_name = '{pkg_name}'
    _launch(launch_file,pkg_name)
      """
      func = func.format(pkg_name=pkg['name'], launch_file=launch_file)
      exec(func)
