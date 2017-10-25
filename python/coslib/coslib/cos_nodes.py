import sys
import click

from coslib.coslib import cos_packages
from coslib.coslib import cos_logging
import subprocess



# def execute(command):
#     process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

#     # Poll process for new output until finished
#     while True:
#         nextline = process.stdout.readline()
#         if nextline == '' and process.poll() is not None:
#             break
#         sys.stdout.write('+EXECUTE output: %s' % nextline)
#         sys.stdout.flush()

#     output = process.communicate()[0]
#     exitCode = process.returncode

#     if (exitCode == 0):
#         return output
#     else:
#         raise ProcessException(command, exitCode, output)

def run(pkg_info, node_config):
  # EXample input (Oct 21, 2017)
  # pkg_info
  # {'launch files': ['/home/dan/co-science-prototype3/packages/my_filters/launch/filters.launch'], 'maintainers': {'name': 'Daniel Snider', 'email': 'danielsnider12@gmail.com'}, 'version': 0.1, 'description': "I'm experimenting still", 'src_sha': 'da39a3ee5e6b4b0d3255bfef95601890afd80709', 'authors': ['Daniel Snider'], 'path': '/home/dan/co-science-prototype3/packages/my_filters', 'nodes': ['/home/dan/co-science-prototype3/packages/my_filters/src/filter.py'], 'name': 'my_filters'}
  # node_config
  # {'params': [{'sigma': 4}], 'name': 'filters', 'file': 'filter.py', 'package': 'my_filters', 'output': [{'image.filter.gaussian': 'gaus'}, 'image.filter.laplace'], 'input': ['image']}

  node_file =  [n for n in pkg_info['nodes'] if node_config['file'] in n]

  if not node_file:
    click.secho('Error: node file not found', fg='red')
    click.secho(node_config['file'], fg='red')
    return

  # if '.py' in node_file:
  #   node_type = 'python'

  cos_logging.logdebug('starting node: %s' % node_file)

    # execute(node_file)

  p = subprocess.Popen(node_file)
  p.wait()
  
  # check available ports
  #   curl http://localhost:8500/v1/catalog/node/laptop

  # create consul service
  # set parametrs on kv store
  # run launch command
