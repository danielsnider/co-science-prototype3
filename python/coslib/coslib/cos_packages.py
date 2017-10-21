import yaml
import glob2
import os
import click

from hashlib import sha1

def collect_package_info():
  # TODO: Don't GLOB 3 times each loop, do it once?
  # TODO: Print warning if too many files detected and slowdown occurs
  # print('searching for packages')
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
  # print('found %s packages.' % len(packages))
  return packages

def get_package_info(package_name):
  pkgs = collect_package_info()
  pkg = [pkg for pkg in pkgs if pkg['name'] == package_name][0]
  return pkg

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

def get_package_src_sha(pkg_name=None, pkg_info=None):
  if not any([pkg_name, pkg_info]):
    raise('Must supply package name of info')
  if not pkg_info:
    pkg_info = get_package_info(pkg_name)

  ## Node Source Hash
  for filename in glob2.iglob(pkg_info['path'] + '/*'):
    # create a hash of of all the file names and file contents for a node's source directory
    node_hash = sha1()
    if os.path.isdir(filename): continue
    with open(filename, "rb") as node_file:
      file_contents = node_file.read()
      node_hash.update(filename)
      node_hash.update(file_contents)
  sha=node_hash.hexdigest()
  return sha


# def get_package_src_tar(........)
  # ## Node Source Tar
  # # TODO: add tar compression
  # file_obj = io.BytesIO() # in memory file to hold tar.bz of node files. Not neccessary to write to disk, it will be written to the database
  # tar_writter = tarfile.open(mode='w', fileobj=file_obj) # create a tar writer
  # tar_writter.add(node['path']) # write tar content to file_obj
  # tar_data = file_obj.getvalue()
  # # write tar data  to db
  # node['source_tar'] = tar_data
  # # If you wish to recover the tar data as a file:
  # # with open('out.tar', "wb") as outfile:
  # #   outfile.write(tar_data)
  # # To untar the archive:
  # # $ tar -xvf out.tar