# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: admobilize/ayuda/v1alpha1/ayuda_service.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2
from admobilize.proto.common import job_pb2 as admobilize_dot_common_dot_job__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='admobilize/ayuda/v1alpha1/ayuda_service.proto',
  package='admobilize.ayuda.v1alpha1',
  syntax='proto3',
  serialized_options=_b('\n\035com.admobilize.ayuda.v1alpha1B\021AyudaServiceProtoP\001\242\002\006ADMAYS\252\002\031AdMobilize.Ayuda.V1Alpha1'),
  serialized_pb=_b('\n-admobilize/ayuda/v1alpha1/ayuda_service.proto\x12\x19\x61\x64mobilize.ayuda.v1alpha1\x1a\x1cgoogle/api/annotations.proto\x1a\x1b\x61\x64mobilize/common/job.proto\"P\n\x0fSnapshotRequest\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x10\n\x08password\x18\x03 \x01(\t\x12\x0c\n\x04\x64\x61te\x18\x04 \x01(\t\"<\n\x18OptimizedSnapshotRequest\x12\x0e\n\x06parent\x18\x01 \x01(\t\x12\x10\n\x08snapshot\x18\x02 \x01(\t\"^\n\rReportRequest\x12\x0e\n\x06parent\x18\x01 \x01(\t\x12\x16\n\x0estart_datetime\x18\x02 \x01(\t\x12\x14\n\x0c\x65nd_datetime\x18\x03 \x01(\t\x12\x0f\n\x07\x64\x65vices\x18\x04 \x03(\t2\x85\x03\n\x0c\x41yudaService\x12p\n\x0e\x43reateSnapshot\x12*.admobilize.ayuda.v1alpha1.SnapshotRequest\x1a\x16.admobilize.common.Job\"\x1a\x82\xd3\xe4\x93\x02\x14\"\x12/v1alpha/snapshots\x12\x82\x01\n\x17\x43reateOptimizedSnapshot\x12\x33.admobilize.ayuda.v1alpha1.OptimizedSnapshotRequest\x1a\x16.admobilize.common.Job\"\x1a\x82\xd3\xe4\x93\x02\x14\"\x12/v1alpha/optimized\x12~\n\x0c\x43reateReport\x12(.admobilize.ayuda.v1alpha1.ReportRequest\x1a\x16.admobilize.common.Job\",\x82\xd3\xe4\x93\x02&\"$/v1alpha/{parent=projects/*}/reportsBY\n\x1d\x63om.admobilize.ayuda.v1alpha1B\x11\x41yudaServiceProtoP\x01\xa2\x02\x06\x41\x44MAYS\xaa\x02\x19\x41\x64Mobilize.Ayuda.V1Alpha1b\x06proto3')
  ,
  dependencies=[google_dot_api_dot_annotations__pb2.DESCRIPTOR,admobilize_dot_common_dot_job__pb2.DESCRIPTOR,])




_SNAPSHOTREQUEST = _descriptor.Descriptor(
  name='SnapshotRequest',
  full_name='admobilize.ayuda.v1alpha1.SnapshotRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='url', full_name='admobilize.ayuda.v1alpha1.SnapshotRequest.url', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='username', full_name='admobilize.ayuda.v1alpha1.SnapshotRequest.username', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='password', full_name='admobilize.ayuda.v1alpha1.SnapshotRequest.password', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='date', full_name='admobilize.ayuda.v1alpha1.SnapshotRequest.date', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=135,
  serialized_end=215,
)


_OPTIMIZEDSNAPSHOTREQUEST = _descriptor.Descriptor(
  name='OptimizedSnapshotRequest',
  full_name='admobilize.ayuda.v1alpha1.OptimizedSnapshotRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='parent', full_name='admobilize.ayuda.v1alpha1.OptimizedSnapshotRequest.parent', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='snapshot', full_name='admobilize.ayuda.v1alpha1.OptimizedSnapshotRequest.snapshot', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=217,
  serialized_end=277,
)


_REPORTREQUEST = _descriptor.Descriptor(
  name='ReportRequest',
  full_name='admobilize.ayuda.v1alpha1.ReportRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='parent', full_name='admobilize.ayuda.v1alpha1.ReportRequest.parent', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='start_datetime', full_name='admobilize.ayuda.v1alpha1.ReportRequest.start_datetime', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='end_datetime', full_name='admobilize.ayuda.v1alpha1.ReportRequest.end_datetime', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='devices', full_name='admobilize.ayuda.v1alpha1.ReportRequest.devices', index=3,
      number=4, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=279,
  serialized_end=373,
)

DESCRIPTOR.message_types_by_name['SnapshotRequest'] = _SNAPSHOTREQUEST
DESCRIPTOR.message_types_by_name['OptimizedSnapshotRequest'] = _OPTIMIZEDSNAPSHOTREQUEST
DESCRIPTOR.message_types_by_name['ReportRequest'] = _REPORTREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

SnapshotRequest = _reflection.GeneratedProtocolMessageType('SnapshotRequest', (_message.Message,), dict(
  DESCRIPTOR = _SNAPSHOTREQUEST,
  __module__ = 'admobilize.ayuda.v1alpha1.ayuda_service_pb2'
  # @@protoc_insertion_point(class_scope:admobilize.ayuda.v1alpha1.SnapshotRequest)
  ))
_sym_db.RegisterMessage(SnapshotRequest)

OptimizedSnapshotRequest = _reflection.GeneratedProtocolMessageType('OptimizedSnapshotRequest', (_message.Message,), dict(
  DESCRIPTOR = _OPTIMIZEDSNAPSHOTREQUEST,
  __module__ = 'admobilize.ayuda.v1alpha1.ayuda_service_pb2'
  # @@protoc_insertion_point(class_scope:admobilize.ayuda.v1alpha1.OptimizedSnapshotRequest)
  ))
_sym_db.RegisterMessage(OptimizedSnapshotRequest)

ReportRequest = _reflection.GeneratedProtocolMessageType('ReportRequest', (_message.Message,), dict(
  DESCRIPTOR = _REPORTREQUEST,
  __module__ = 'admobilize.ayuda.v1alpha1.ayuda_service_pb2'
  # @@protoc_insertion_point(class_scope:admobilize.ayuda.v1alpha1.ReportRequest)
  ))
_sym_db.RegisterMessage(ReportRequest)


DESCRIPTOR._options = None

_AYUDASERVICE = _descriptor.ServiceDescriptor(
  name='AyudaService',
  full_name='admobilize.ayuda.v1alpha1.AyudaService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=376,
  serialized_end=765,
  methods=[
  _descriptor.MethodDescriptor(
    name='CreateSnapshot',
    full_name='admobilize.ayuda.v1alpha1.AyudaService.CreateSnapshot',
    index=0,
    containing_service=None,
    input_type=_SNAPSHOTREQUEST,
    output_type=admobilize_dot_common_dot_job__pb2._JOB,
    serialized_options=_b('\202\323\344\223\002\024\"\022/v1alpha/snapshots'),
  ),
  _descriptor.MethodDescriptor(
    name='CreateOptimizedSnapshot',
    full_name='admobilize.ayuda.v1alpha1.AyudaService.CreateOptimizedSnapshot',
    index=1,
    containing_service=None,
    input_type=_OPTIMIZEDSNAPSHOTREQUEST,
    output_type=admobilize_dot_common_dot_job__pb2._JOB,
    serialized_options=_b('\202\323\344\223\002\024\"\022/v1alpha/optimized'),
  ),
  _descriptor.MethodDescriptor(
    name='CreateReport',
    full_name='admobilize.ayuda.v1alpha1.AyudaService.CreateReport',
    index=2,
    containing_service=None,
    input_type=_REPORTREQUEST,
    output_type=admobilize_dot_common_dot_job__pb2._JOB,
    serialized_options=_b('\202\323\344\223\002&\"$/v1alpha/{parent=projects/*}/reports'),
  ),
])
_sym_db.RegisterServiceDescriptor(_AYUDASERVICE)

DESCRIPTOR.services_by_name['AyudaService'] = _AYUDASERVICE

# @@protoc_insertion_point(module_scope)
