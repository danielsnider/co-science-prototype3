import os
import tables


class CacheService():
  def __init__(self, node_name, pkg_info, hdf5_path=None):
    self.work_dir = '.'
    self.hdf5_path = hdf5_path or os.path.join(self.work_dir,'%s_cache.h5' % node_name)
    self.hdf5_file = tables.open_file(self.hdf5_path,'w') # TEST: does not overwrite existing?
    self.group_name = 'ver_%s' % pkg_info['src_sha']
    self.group = self.hdf5_file.create_group('/', self.group_name, 'Cache')

  def lookup_mem_hdf5(self, request):
    # NOT IMPLEMENTED
    # Does pytables cache recently used in memory?
    return False

  def lookup_disk_hdf5(self, request):
    node_name = '/%s/%s' % (self.group_name, request)
    try:
      node = self.hdf5_file.get_node(node_name)
      return node
    except tables.exceptions.NoSuchNodeError:
      return None

  def lookup(self, request):
    return self.lookup_mem_hdf5(request) or \
           self.lookup_disk_hdf5(request)

  def queue_cache_entry(self, request, result):
    pass

  def insert_cache_entry(self, request, result):
    where = '/%s' % self.group_name
    self.hdf5_file.create_array(where, request, result)
    self.hdf5_file.flush()

  def close(self):
    self.hdf5_file.close()
