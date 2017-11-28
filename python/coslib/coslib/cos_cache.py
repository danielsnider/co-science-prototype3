import os
import tables
import cos

class CacheService():
  def __init__(self, node_name, pkg_info, hdf5_path=None):
    self.cache_enabled = True
    self.work_dir = '.'
    self.hdf5_path = hdf5_path or os.path.join(self.work_dir,'%s_cache.h5' % node_name)
    self.hdf5_file = tables.open_file(self.hdf5_path,'a') # TEST: does not overwrite existing?
    self.group_name = 'ver_%s' % pkg_info['src_sha']
    try:
      self.group = self.hdf5_file.create_group('/', self.group_name, 'Cache')
    except tables.exceptions.NodeError:
      pass

  def lookup_mem_hdf5(self, request):
    # NOT IMPLEMENTED
    # Does pytables cache recently used in memory?
    return False

  def lookup_disk_hdf5(self, request):
    node_name = '/%s/%s' % (self.group_name, request)
    try:
      node = self.hdf5_file.get_node(node_name)
      cos.logdebug("[CACHE] hit for request %s" % request)
      return node
    except tables.exceptions.NoSuchNodeError:
      cos.logdebug('[CACHE] Miss. Could not find cache entry at node named "%s"' % node_name)
      cos.logdebug('[CACHE] I have available\n%s' % self.hdf5_file.list_nodes('/'))
      return None

  def lookup(self, request):
    if self.cache_enabled:
      return self.lookup_mem_hdf5(request) or \
             self.lookup_disk_hdf5(request)

  def queue_cache_entry(self, request, result):
    pass

  def insert_cache_entry(self, request, result):
    where = '/%s' % self.group_name
    # key = request
    # from IPython import embed
    # embed() # drop into an IPython session
    # value = result.read()
    # cos.loginfo('value.__class__')
    # cos.loginfo(value.__class__)
    # result.copy(self.hdf5_file.create_array(where, key, []))
    result.copy(eval('self.hdf5_file.root.%s' % where[1:]))
    # self.hdf5_file.create_array(where, key, value)
    # result._v_attrs._f_copy(eval('self.hdf5_file.root.%s.%s'%(where[1:],key)))
    self.hdf5_file.flush()

  def close(self):
    self.hdf5_file.close()

