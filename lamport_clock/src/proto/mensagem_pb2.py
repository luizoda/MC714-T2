# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/mensagem.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14proto/mensagem.proto\x12\rlamport_clock\" \n\x0bTimeRequest\x12\x11\n\ttimestamp\x18\x01 \x01(\x05\"\x0e\n\x0cTimeResponse2J\n\x05\x43lock\x12\x41\n\x04Time\x12\x1a.lamport_clock.TimeRequest\x1a\x1b.lamport_clock.TimeResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.mensagem_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_TIMEREQUEST']._serialized_start=39
  _globals['_TIMEREQUEST']._serialized_end=71
  _globals['_TIMERESPONSE']._serialized_start=73
  _globals['_TIMERESPONSE']._serialized_end=87
  _globals['_CLOCK']._serialized_start=89
  _globals['_CLOCK']._serialized_end=163
# @@protoc_insertion_point(module_scope)
