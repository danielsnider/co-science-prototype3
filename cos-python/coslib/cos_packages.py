import yaml
import glob2
import os

def collect_package_info():
  conf = yaml.load(file('/etc/cos/config.yaml', 'r'))
  packages = []
  for pkg_path in conf['package paths']:
    for pkg_conf_file in glob2.glob('%s/**/*cos-package.yaml' % pkg_path, recursive=True):
      found_pkg_path = os.path.dirname(pkg_conf_file) # found a folder with the correct yaml
      pkg = yaml.load(file(pkg_conf_file, 'r'))
      pkg['path'] = found_pkg_path
      # Find executable nodes in 'src' directory
      pkg['nodes'] = []
      for src_file in glob2.glob('%s/src/**/*' % found_pkg_path, recursive=True):
        if os.access(src_file, os.X_OK): # check if executable
          pkg['nodes'].append(src_file)
      pkg['launch files'] = []
      # Find launch files in 'launch' directory
      for src_file in glob2.glob('%s/launch/**/*.launch' % found_pkg_path, recursive=True):
        pkg['launch files'].append(src_file)
      packages.append(pkg)
  return packages


# EXAMPLE RETURN VALUE
# [{'authors': ['Daniel Snider'],
#   'description': "I'm experimenting still",
#   'maintainers': {'email': 'danielsnider12@gmail.com',
#                   'name': 'Daniel Snider'},
#   'name': 'builtin',
#   'nodes': ['/home/dan/co-science-prototype3/src/viewer.py',
#             '/home/dan/co-science-prototype3/src/filter.py',
#             '/home/dan/co-science-prototype3/src/reader.py'],
#   'path': '/home/dan/co-science-prototype3',
#   'version': 0.1},
#  {'authors': ['Daniel Snider'],
#   'description': "I'm experimenting still",
#   'maintainers': {'email': 'danielsnider12@gmail.com',
#                   'name': 'Daniel Snider'},
#   'name': 'builtin',
#   'nodes': [],
#   'path': '/home/dan/co-science-prototype3/temp',
#   'version': 0.1}]
