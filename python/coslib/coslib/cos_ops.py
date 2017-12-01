
###
### GET (previously REQUEST)
###
def get(topic, selector):
  # do ids_ready, ids_not_ready = selector_to_ids(topic,selector)
  try:
    topic_url = topic_to_rpc_url(topic)
    logdebug('requesting on topic %s' % topic_url)
    channel_stub = create_grpc_channel_at(topic_url)
    response = channel_stub.GetAsset(HDF5_pb2.AssetRequest(selector=selector))
    if response.message == 'None':
      return
    im = hdf5_response_to_im(response)
    return im
  except grpc._channel._Rendezvous as e:
    global node_name
    err_msg = e._state.details.split('Exception calling application: ')[-1]
    logerr('Error in node: %s. Message: "%s"' % (node_name,err_msg))
    if err_msg == 'Connect Failed':
      logerr("Is the rode running? Is it reachable on its assigned address of '%s'?" % topic_url)
    # raise e   # Don't raise a stacktrace here, it wasn't us, it was the other node
  except Exception as e:
    global node_name
    logerr('Error in node: %s' % node_name)
    raise e


def selector_to_ids(topic, selector):
  pass
  # for each selector requirement bulk_id_check(topic,selector) against consumer/prosumers involved, returned data includes:
    # ids_ok - ids in cache and meets selector requirements (eg. quality>90)
    # ids_not_ok - ids in cache and does not meet selector requirements
    # ids_not_computed - ids not yet in cache, and unknown if it meets selector
    # if node not available, return error
  # union ids_ok from each node
  # return ids_ok so that work can begin (or do usercallback with data)
  # count ids_ok
  # while ids_not_computed and selector unmet:
    # for contstraint in selector:
      # if cos.get(contstaint_topic, id_not_computed) is OK:
        # return another id_ok and increase count (or do usercallback with data)


def put(topic, fields):
  pass

def delete(selector):
  pass

def watch(topic):
  pass