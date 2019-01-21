# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: admobilize/devicemanagement/v1alpha2/resources.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from admobilize.proto.common import entity_pb2 as admobilize_dot_common_dot_entity__pb2
from admobilize.proto.billing.v1alpha1 import billing_pb2 as admobilize_dot_billing_dot_v1alpha1_dot_billing__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='admobilize/devicemanagement/v1alpha2/resources.proto',
  package='admobilize.devicemanagement.v1alpha2',
  syntax='proto3',
  serialized_options=_b('\n(com.admobilize.devicemanagement.v1alpha2B\013DeviceProtoP\001\242\002\005ADMDM\252\002$AdMobilize.DeviceManagement.V1Alpha2'),
  serialized_pb=_b('\n4admobilize/devicemanagement/v1alpha2/resources.proto\x12$admobilize.devicemanagement.v1alpha2\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1e\x61\x64mobilize/common/entity.proto\x1a)admobilize/billing/v1alpha1/billing.proto\"G\n\x03\x41\x63l\x12\x10\n\x08owner_id\x18\x01 \x01(\t\x12\x12\n\nproject_id\x18\x02 \x01(\t\x12\x1a\n\x12provisioning_token\x18\x03 \x01(\t\"1\n\nPermission\x12\x12\n\npermission\x18\x01 \x01(\t\x12\x0f\n\x07members\x18\x02 \x03(\t\"\x81\x01\n\nProjectAcl\x12\x10\n\x08owner_id\x18\x01 \x01(\t\x12\x1a\n\x12provisioning_token\x18\x02 \x01(\t\x12\x45\n\x0bpermissions\x18\n \x03(\x0b\x32\x30.admobilize.devicemanagement.v1alpha2.Permission\"\xc9\x02\n\x07Project\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x14\n\x0c\x64isplay_name\x18\x03 \x01(\t\x12=\n\x03\x61\x63l\x18\x04 \x01(\x0b\x32\x30.admobilize.devicemanagement.v1alpha2.ProjectAcl\x12\x44\n\x0f\x62illing_account\x18\x05 \x01(\x0b\x32+.admobilize.billing.v1alpha1.BillingAccount\x12\x0f\n\x07\x64\x65vices\x18\n \x03(\t\x12I\n\x06labels\x18\x14 \x03(\x0b\x32\x39.admobilize.devicemanagement.v1alpha2.Project.LabelsEntry\x1a-\n\x0bLabelsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\x1f\n\x0f\x41pplicationMeta\x12\x0c\n\x04name\x18\x01 \x01(\t\"\xc1\x01\n\x0b\x41pplication\x12\n\n\x02id\x18\x01 \x01(\t\x12\x36\n\x03\x61\x63l\x18\x04 \x01(\x0b\x32).admobilize.devicemanagement.v1alpha2.Acl\x12)\n\x06\x63onfig\x18\x05 \x01(\x0b\x32\x19.admobilize.common.Entity\x12\x43\n\x04meta\x18\x06 \x01(\x0b\x32\x35.admobilize.devicemanagement.v1alpha2.ApplicationMeta\"1\n\x0c\x44\x65viceConfig\x12\x13\n\x0b\x61uto_update\x18\x01 \x01(\x08\x12\x0c\n\x04init\x18\x02 \x03(\t\"\xba\x02\n\nDeviceMeta\x12/\n\x0b\x63reate_time\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12/\n\x0bupdate_time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x14\n\x0c\x64isplay_name\x18\x03 \x01(\t\x12\x0c\n\x04type\x18\x04 \x01(\t\x12L\n\x06labels\x18\x05 \x03(\x0b\x32<.admobilize.devicemanagement.v1alpha2.DeviceMeta.LabelsEntry\x12\x15\n\rmqtt_registry\x18\x06 \x01(\t\x12\x12\n\npublic_key\x18\x07 \x01(\t\x1a-\n\x0bLabelsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\xa7\x02\n\x06\x44\x65vice\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x36\n\x03\x61\x63l\x18\x03 \x01(\x0b\x32).admobilize.devicemanagement.v1alpha2.Acl\x12\x42\n\x06\x63onfig\x18\x04 \x01(\x0b\x32\x32.admobilize.devicemanagement.v1alpha2.DeviceConfig\x12>\n\x04meta\x18\x05 \x01(\x0b\x32\x30.admobilize.devicemanagement.v1alpha2.DeviceMeta\x12G\n\x0c\x61pplications\x18\x06 \x03(\x0b\x32\x31.admobilize.devicemanagement.v1alpha2.ApplicationBh\n(com.admobilize.devicemanagement.v1alpha2B\x0b\x44\x65viceProtoP\x01\xa2\x02\x05\x41\x44MDM\xaa\x02$AdMobilize.DeviceManagement.V1Alpha2b\x06proto3')
  ,
  dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,admobilize_dot_common_dot_entity__pb2.DESCRIPTOR,admobilize_dot_billing_dot_v1alpha1_dot_billing__pb2.DESCRIPTOR,])




_ACL = _descriptor.Descriptor(
  name='Acl',
  full_name='admobilize.devicemanagement.v1alpha2.Acl',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='owner_id', full_name='admobilize.devicemanagement.v1alpha2.Acl.owner_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='project_id', full_name='admobilize.devicemanagement.v1alpha2.Acl.project_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='provisioning_token', full_name='admobilize.devicemanagement.v1alpha2.Acl.provisioning_token', index=2,
      number=3, type=9, cpp_type=9, label=1,
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
  serialized_start=202,
  serialized_end=273,
)


_PERMISSION = _descriptor.Descriptor(
  name='Permission',
  full_name='admobilize.devicemanagement.v1alpha2.Permission',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='permission', full_name='admobilize.devicemanagement.v1alpha2.Permission.permission', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='members', full_name='admobilize.devicemanagement.v1alpha2.Permission.members', index=1,
      number=2, type=9, cpp_type=9, label=3,
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
  serialized_start=275,
  serialized_end=324,
)


_PROJECTACL = _descriptor.Descriptor(
  name='ProjectAcl',
  full_name='admobilize.devicemanagement.v1alpha2.ProjectAcl',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='owner_id', full_name='admobilize.devicemanagement.v1alpha2.ProjectAcl.owner_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='provisioning_token', full_name='admobilize.devicemanagement.v1alpha2.ProjectAcl.provisioning_token', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='permissions', full_name='admobilize.devicemanagement.v1alpha2.ProjectAcl.permissions', index=2,
      number=10, type=11, cpp_type=10, label=3,
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
  serialized_start=327,
  serialized_end=456,
)


_PROJECT_LABELSENTRY = _descriptor.Descriptor(
  name='LabelsEntry',
  full_name='admobilize.devicemanagement.v1alpha2.Project.LabelsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='admobilize.devicemanagement.v1alpha2.Project.LabelsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='admobilize.devicemanagement.v1alpha2.Project.LabelsEntry.value', index=1,
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
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=743,
  serialized_end=788,
)

_PROJECT = _descriptor.Descriptor(
  name='Project',
  full_name='admobilize.devicemanagement.v1alpha2.Project',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='admobilize.devicemanagement.v1alpha2.Project.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='name', full_name='admobilize.devicemanagement.v1alpha2.Project.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='display_name', full_name='admobilize.devicemanagement.v1alpha2.Project.display_name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='acl', full_name='admobilize.devicemanagement.v1alpha2.Project.acl', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='billing_account', full_name='admobilize.devicemanagement.v1alpha2.Project.billing_account', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='devices', full_name='admobilize.devicemanagement.v1alpha2.Project.devices', index=5,
      number=10, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='labels', full_name='admobilize.devicemanagement.v1alpha2.Project.labels', index=6,
      number=20, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_PROJECT_LABELSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=459,
  serialized_end=788,
)


_APPLICATIONMETA = _descriptor.Descriptor(
  name='ApplicationMeta',
  full_name='admobilize.devicemanagement.v1alpha2.ApplicationMeta',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='admobilize.devicemanagement.v1alpha2.ApplicationMeta.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
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
  serialized_start=790,
  serialized_end=821,
)


_APPLICATION = _descriptor.Descriptor(
  name='Application',
  full_name='admobilize.devicemanagement.v1alpha2.Application',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='admobilize.devicemanagement.v1alpha2.Application.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='acl', full_name='admobilize.devicemanagement.v1alpha2.Application.acl', index=1,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='config', full_name='admobilize.devicemanagement.v1alpha2.Application.config', index=2,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='meta', full_name='admobilize.devicemanagement.v1alpha2.Application.meta', index=3,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=824,
  serialized_end=1017,
)


_DEVICECONFIG = _descriptor.Descriptor(
  name='DeviceConfig',
  full_name='admobilize.devicemanagement.v1alpha2.DeviceConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='auto_update', full_name='admobilize.devicemanagement.v1alpha2.DeviceConfig.auto_update', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='init', full_name='admobilize.devicemanagement.v1alpha2.DeviceConfig.init', index=1,
      number=2, type=9, cpp_type=9, label=3,
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
  serialized_start=1019,
  serialized_end=1068,
)


_DEVICEMETA_LABELSENTRY = _descriptor.Descriptor(
  name='LabelsEntry',
  full_name='admobilize.devicemanagement.v1alpha2.DeviceMeta.LabelsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='admobilize.devicemanagement.v1alpha2.DeviceMeta.LabelsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='admobilize.devicemanagement.v1alpha2.DeviceMeta.LabelsEntry.value', index=1,
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
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=743,
  serialized_end=788,
)

_DEVICEMETA = _descriptor.Descriptor(
  name='DeviceMeta',
  full_name='admobilize.devicemanagement.v1alpha2.DeviceMeta',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='create_time', full_name='admobilize.devicemanagement.v1alpha2.DeviceMeta.create_time', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='update_time', full_name='admobilize.devicemanagement.v1alpha2.DeviceMeta.update_time', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='display_name', full_name='admobilize.devicemanagement.v1alpha2.DeviceMeta.display_name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='type', full_name='admobilize.devicemanagement.v1alpha2.DeviceMeta.type', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='labels', full_name='admobilize.devicemanagement.v1alpha2.DeviceMeta.labels', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='mqtt_registry', full_name='admobilize.devicemanagement.v1alpha2.DeviceMeta.mqtt_registry', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='public_key', full_name='admobilize.devicemanagement.v1alpha2.DeviceMeta.public_key', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_DEVICEMETA_LABELSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1071,
  serialized_end=1385,
)


_DEVICE = _descriptor.Descriptor(
  name='Device',
  full_name='admobilize.devicemanagement.v1alpha2.Device',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='admobilize.devicemanagement.v1alpha2.Device.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='name', full_name='admobilize.devicemanagement.v1alpha2.Device.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='acl', full_name='admobilize.devicemanagement.v1alpha2.Device.acl', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='config', full_name='admobilize.devicemanagement.v1alpha2.Device.config', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='meta', full_name='admobilize.devicemanagement.v1alpha2.Device.meta', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='applications', full_name='admobilize.devicemanagement.v1alpha2.Device.applications', index=5,
      number=6, type=11, cpp_type=10, label=3,
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
  serialized_start=1388,
  serialized_end=1683,
)

_PROJECTACL.fields_by_name['permissions'].message_type = _PERMISSION
_PROJECT_LABELSENTRY.containing_type = _PROJECT
_PROJECT.fields_by_name['acl'].message_type = _PROJECTACL
_PROJECT.fields_by_name['billing_account'].message_type = admobilize_dot_billing_dot_v1alpha1_dot_billing__pb2._BILLINGACCOUNT
_PROJECT.fields_by_name['labels'].message_type = _PROJECT_LABELSENTRY
_APPLICATION.fields_by_name['acl'].message_type = _ACL
_APPLICATION.fields_by_name['config'].message_type = admobilize_dot_common_dot_entity__pb2._ENTITY
_APPLICATION.fields_by_name['meta'].message_type = _APPLICATIONMETA
_DEVICEMETA_LABELSENTRY.containing_type = _DEVICEMETA
_DEVICEMETA.fields_by_name['create_time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_DEVICEMETA.fields_by_name['update_time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_DEVICEMETA.fields_by_name['labels'].message_type = _DEVICEMETA_LABELSENTRY
_DEVICE.fields_by_name['acl'].message_type = _ACL
_DEVICE.fields_by_name['config'].message_type = _DEVICECONFIG
_DEVICE.fields_by_name['meta'].message_type = _DEVICEMETA
_DEVICE.fields_by_name['applications'].message_type = _APPLICATION
DESCRIPTOR.message_types_by_name['Acl'] = _ACL
DESCRIPTOR.message_types_by_name['Permission'] = _PERMISSION
DESCRIPTOR.message_types_by_name['ProjectAcl'] = _PROJECTACL
DESCRIPTOR.message_types_by_name['Project'] = _PROJECT
DESCRIPTOR.message_types_by_name['ApplicationMeta'] = _APPLICATIONMETA
DESCRIPTOR.message_types_by_name['Application'] = _APPLICATION
DESCRIPTOR.message_types_by_name['DeviceConfig'] = _DEVICECONFIG
DESCRIPTOR.message_types_by_name['DeviceMeta'] = _DEVICEMETA
DESCRIPTOR.message_types_by_name['Device'] = _DEVICE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Acl = _reflection.GeneratedProtocolMessageType('Acl', (_message.Message,), dict(
  DESCRIPTOR = _ACL,
  __module__ = 'admobilize.devicemanagement.v1alpha2.resources_pb2'
  # @@protoc_insertion_point(class_scope:admobilize.devicemanagement.v1alpha2.Acl)
  ))
_sym_db.RegisterMessage(Acl)

Permission = _reflection.GeneratedProtocolMessageType('Permission', (_message.Message,), dict(
  DESCRIPTOR = _PERMISSION,
  __module__ = 'admobilize.devicemanagement.v1alpha2.resources_pb2'
  # @@protoc_insertion_point(class_scope:admobilize.devicemanagement.v1alpha2.Permission)
  ))
_sym_db.RegisterMessage(Permission)

ProjectAcl = _reflection.GeneratedProtocolMessageType('ProjectAcl', (_message.Message,), dict(
  DESCRIPTOR = _PROJECTACL,
  __module__ = 'admobilize.devicemanagement.v1alpha2.resources_pb2'
  # @@protoc_insertion_point(class_scope:admobilize.devicemanagement.v1alpha2.ProjectAcl)
  ))
_sym_db.RegisterMessage(ProjectAcl)

Project = _reflection.GeneratedProtocolMessageType('Project', (_message.Message,), dict(

  LabelsEntry = _reflection.GeneratedProtocolMessageType('LabelsEntry', (_message.Message,), dict(
    DESCRIPTOR = _PROJECT_LABELSENTRY,
    __module__ = 'admobilize.devicemanagement.v1alpha2.resources_pb2'
    # @@protoc_insertion_point(class_scope:admobilize.devicemanagement.v1alpha2.Project.LabelsEntry)
    ))
  ,
  DESCRIPTOR = _PROJECT,
  __module__ = 'admobilize.devicemanagement.v1alpha2.resources_pb2'
  # @@protoc_insertion_point(class_scope:admobilize.devicemanagement.v1alpha2.Project)
  ))
_sym_db.RegisterMessage(Project)
_sym_db.RegisterMessage(Project.LabelsEntry)

ApplicationMeta = _reflection.GeneratedProtocolMessageType('ApplicationMeta', (_message.Message,), dict(
  DESCRIPTOR = _APPLICATIONMETA,
  __module__ = 'admobilize.devicemanagement.v1alpha2.resources_pb2'
  # @@protoc_insertion_point(class_scope:admobilize.devicemanagement.v1alpha2.ApplicationMeta)
  ))
_sym_db.RegisterMessage(ApplicationMeta)

Application = _reflection.GeneratedProtocolMessageType('Application', (_message.Message,), dict(
  DESCRIPTOR = _APPLICATION,
  __module__ = 'admobilize.devicemanagement.v1alpha2.resources_pb2'
  # @@protoc_insertion_point(class_scope:admobilize.devicemanagement.v1alpha2.Application)
  ))
_sym_db.RegisterMessage(Application)

DeviceConfig = _reflection.GeneratedProtocolMessageType('DeviceConfig', (_message.Message,), dict(
  DESCRIPTOR = _DEVICECONFIG,
  __module__ = 'admobilize.devicemanagement.v1alpha2.resources_pb2'
  # @@protoc_insertion_point(class_scope:admobilize.devicemanagement.v1alpha2.DeviceConfig)
  ))
_sym_db.RegisterMessage(DeviceConfig)

DeviceMeta = _reflection.GeneratedProtocolMessageType('DeviceMeta', (_message.Message,), dict(

  LabelsEntry = _reflection.GeneratedProtocolMessageType('LabelsEntry', (_message.Message,), dict(
    DESCRIPTOR = _DEVICEMETA_LABELSENTRY,
    __module__ = 'admobilize.devicemanagement.v1alpha2.resources_pb2'
    # @@protoc_insertion_point(class_scope:admobilize.devicemanagement.v1alpha2.DeviceMeta.LabelsEntry)
    ))
  ,
  DESCRIPTOR = _DEVICEMETA,
  __module__ = 'admobilize.devicemanagement.v1alpha2.resources_pb2'
  # @@protoc_insertion_point(class_scope:admobilize.devicemanagement.v1alpha2.DeviceMeta)
  ))
_sym_db.RegisterMessage(DeviceMeta)
_sym_db.RegisterMessage(DeviceMeta.LabelsEntry)

Device = _reflection.GeneratedProtocolMessageType('Device', (_message.Message,), dict(
  DESCRIPTOR = _DEVICE,
  __module__ = 'admobilize.devicemanagement.v1alpha2.resources_pb2'
  # @@protoc_insertion_point(class_scope:admobilize.devicemanagement.v1alpha2.Device)
  ))
_sym_db.RegisterMessage(Device)


DESCRIPTOR._options = None
_PROJECT_LABELSENTRY._options = None
_DEVICEMETA_LABELSENTRY._options = None
# @@protoc_insertion_point(module_scope)
