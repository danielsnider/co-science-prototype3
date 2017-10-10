import os
import click

@click.group()
def launch():
    pass

dirs = '/home/dan/co-science-prototype3/click-tests/pkgs/'
pkgs = os.listdir(dirs)

for pkg in pkgs:
  func = """@launch.group()
@click.option('--count', default=1, help='Number of greetings.')
def {pkg}(count):
    pass
  """
  func = func.format(pkg=pkg)
  exec(func)

  nodes = os.listdir(dirs + pkg)
  for node in nodes:
      func = """@{pkg}.command()
@click.option('--count', default=1, help='Number of greetings.')
def {node}(count):
    node = '{node}'
    pkg = '{pkg}'
    print('launching node %s from package %s' %(node,pkg))
      """
      func = func.format(pkg=pkg, node=node)
      exec(func)
