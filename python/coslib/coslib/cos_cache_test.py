import cos_cache as c
pkg_info  = {'src_sha': 'eontue9u409'}

cs = c.CacheService('my_node',pkg_info)
cs.lookup('cat')
cs.insert_cache_entry('cat','meow')
cs.lookup('cat')

# im = self.callback(request)
# return HDF5_pb2.AssetReply(message=data)

