# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: HDF5.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='HDF5.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\nHDF5.proto\"\x1d\n\x0f\x41ssetIdentifier\x12\n\n\x02id\x18\x01 \x01(\t\"\x1c\n\tHDF5Reply\x12\x0f\n\x07message\x18\x01 \x01(\t22\n\x05\x41sset\x12)\n\x07Request\x12\x10.AssetIdentifier\x1a\n.HDF5Reply\"\x00\x62\x06proto3')
)




_ASSETIDENTIFIER = _descriptor.Descriptor(
  name='AssetIdentifier',
  full_name='AssetIdentifier',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='AssetIdentifier.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=14,
  serialized_end=43,
)


_HDF5REPLY = _descriptor.Descriptor(
  name='HDF5Reply',
  full_name='HDF5Reply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message', full_name='HDF5Reply.message', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=45,
  serialized_end=73,
)

DESCRIPTOR.message_types_by_name['AssetIdentifier'] = _ASSETIDENTIFIER
DESCRIPTOR.message_types_by_name['HDF5Reply'] = _HDF5REPLY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

AssetIdentifier = _reflection.GeneratedProtocolMessageType('AssetIdentifier', (_message.Message,), dict(
  DESCRIPTOR = _ASSETIDENTIFIER,
  __module__ = 'HDF5_pb2'
  # @@protoc_insertion_point(class_scope:AssetIdentifier)
  ))
_sym_db.RegisterMessage(AssetIdentifier)

HDF5Reply = _reflection.GeneratedProtocolMessageType('HDF5Reply', (_message.Message,), dict(
  DESCRIPTOR = _HDF5REPLY,
  __module__ = 'HDF5_pb2'
  # @@protoc_insertion_point(class_scope:HDF5Reply)
  ))
_sym_db.RegisterMessage(HDF5Reply)



_ASSET = _descriptor.ServiceDescriptor(
  name='Asset',
  full_name='Asset',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=75,
  serialized_end=125,
  methods=[
  _descriptor.MethodDescriptor(
    name='Request',
    full_name='Asset.Request',
    index=0,
    containing_service=None,
    input_type=_ASSETIDENTIFIER,
    output_type=_HDF5REPLY,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_ASSET)

DESCRIPTOR.services_by_name['Asset'] = _ASSET

try:
  # THESE ELEMENTS WILL BE DEPRECATED.
  # Please use the generated *_pb2_grpc.py files instead.
  import grpc
  from grpc.beta import implementations as beta_implementations
  from grpc.beta import interfaces as beta_interfaces
  from grpc.framework.common import cardinality
  from grpc.framework.interfaces.face import utilities as face_utilities


  class AssetStub(object):
    """The greeting service definition.
    """

    def __init__(self, channel):
      """Constructor.

      Args:
        channel: A grpc.Channel.
      """
      self.Request = channel.unary_unary(
          '/Asset/Request',
          request_serializer=AssetIdentifier.SerializeToString,
          response_deserializer=HDF5Reply.FromString,
          )


  class AssetServicer(object):
    """The greeting service definition.
    """

    def Request(self, request, context):
      """Sends a greeting
      """
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')


  def add_AssetServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'Request': grpc.unary_unary_rpc_method_handler(
            servicer.Request,
            request_deserializer=AssetIdentifier.FromString,
            response_serializer=HDF5Reply.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'Asset', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


  class BetaAssetServicer(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    """The greeting service definition.
    """
    def Request(self, request, context):
      """Sends a greeting
      """
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)


  class BetaAssetStub(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    """The greeting service definition.
    """
    def Request(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      """Sends a greeting
      """
      raise NotImplementedError()
    Request.future = None


  def beta_create_Asset_server(servicer, pool=None, pool_size=None, default_timeout=None, maximum_timeout=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_deserializers = {
      ('Asset', 'Request'): AssetIdentifier.FromString,
    }
    response_serializers = {
      ('Asset', 'Request'): HDF5Reply.SerializeToString,
    }
    method_implementations = {
      ('Asset', 'Request'): face_utilities.unary_unary_inline(servicer.Request),
    }
    server_options = beta_implementations.server_options(request_deserializers=request_deserializers, response_serializers=response_serializers, thread_pool=pool, thread_pool_size=pool_size, default_timeout=default_timeout, maximum_timeout=maximum_timeout)
    return beta_implementations.server(method_implementations, options=server_options)


  def beta_create_Asset_stub(channel, host=None, metadata_transformer=None, pool=None, pool_size=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_serializers = {
      ('Asset', 'Request'): AssetIdentifier.SerializeToString,
    }
    response_deserializers = {
      ('Asset', 'Request'): HDF5Reply.FromString,
    }
    cardinalities = {
      'Request': cardinality.Cardinality.UNARY_UNARY,
    }
    stub_options = beta_implementations.stub_options(host=host, metadata_transformer=metadata_transformer, request_serializers=request_serializers, response_deserializers=response_deserializers, thread_pool=pool, thread_pool_size=pool_size)
    return beta_implementations.dynamic_stub(channel, 'Asset', cardinalities, options=stub_options)
except ImportError:
  pass
# @@protoc_insertion_point(module_scope)