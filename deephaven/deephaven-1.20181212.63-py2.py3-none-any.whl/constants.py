#
# Copyright (c) 2016-2017 Illumon and Patent Pending
#

import numpy as np;

java_type_map = {}
java_array_types = {}
null_values = {}


NULL_CHAR = 65534
NULL_FLOAT = float.fromhex('-0x1.fffffep127')
NULL_DOUBLE = float.fromhex('-0x1.fffffffffffffP+1023')
NULL_SHORT = -32768
NULL_INT = -0x80000000
NULL_LONG = -0x8000000000000000
NULL_BYTE = -128

# These maps are used for conversions between columns from Deephaven tables and Numpy arrays
java_type_map = {
    'char' : np.object,
    'float' : np.float32,
    'double' : np.float64,
    'short' : np.int16,
    'int' : np.int32,
    'long' : np.int64,
    'byte' : np.int8,
    'object' : np.object,
    'boolean' : np.bool_,
    'java.lang.Boolean' : np.bool_
}

java_array_types = {
    'float' : '[F',
    'double' : '[D',
    'short' : '[S',
    'int' : '[I',
    'long' : '[J',
    'byte' : '[B',
    'object' : '[Ljava.lang.String;',
    'boolean' : '[Z',
    'java.lang.Boolean' : '[Z',
    'java.lang.String' : '[Ljava.lang.String;'
}

null_values = {
    'char' : NULL_CHAR,
    'float' :  NULL_FLOAT,
    'double' : NULL_DOUBLE,
    'short' :  NULL_SHORT,
    'int' : NULL_INT,
    'long' :  NULL_LONG,
    'byte' : NULL_BYTE,
    'java.lang.Boolean' : None,
    'object' : None
}

dtype_to_columnsource_and_type = {
    'bool_': ('com.illumon.iris.db.v2.sources.immutable.ImmutableBooleanArraySource', 'boolean'),
    'numpy.bool_': ('com.illumon.iris.db.v2.sources.immutable.ImmutableBooleanArraySource', 'boolean'),
    'bool': ('com.illumon.iris.db.v2.sources.immutable.ImmutableBooleanArraySource', 'boolean'),
    'int_': ('com.illumon.iris.db.v2.sources.immutable.ImmutableIntArraySource', 'int'),
    'intc': ('com.illumon.iris.db.v2.sources.immutable.ImmutableIntArraySource', 'int'),
    'intp': ('com.illumon.iris.db.v2.sources.immutable.ImmutableIntArraySource', 'int'),
    'int8': ('com.illumon.iris.db.v2.sources.immutable.ImmutableByteArraySource', 'byte'),
    'int16': ('com.illumon.iris.db.v2.sources.immutable.ImmutableShortArraySource', 'short'),
    'int32': ('com.illumon.iris.db.v2.sources.immutable.ImmutableIntArraySource', 'int'),
    'int64': ('com.illumon.iris.db.v2.sources.immutable.ImmutableLongArraySource', 'long'),
    'uint8': ('com.illumon.iris.db.v2.sources.immutable.ImmutableByteArraySource', 'byte'),
    'uint16': ('com.illumon.iris.db.v2.sources.immutable.ImmutableIntArraySource', 'int'),
    'uint32': ('com.illumon.iris.db.v2.sources.immutable.ImmutableLongArraySource', 'long'),
    'uint64': ('com.illumon.iris.db.v2.sources.immutable.ImmutableObjectArraySource', 'java.lang.String'),
    'float_': ('com.illumon.iris.db.v2.sources.immutable.ImmutableDoubleArraySource', 'double'),
    'float16': ('com.illumon.iris.db.v2.sources.immutable.ImmutableFloatArraySource', 'float'),
    'float32': ('com.illumon.iris.db.v2.sources.immutable.ImmutableFloatArraySource', 'float'),
    'float64': ('com.illumon.iris.db.v2.sources.immutable.ImmutableDoubleArraySource', 'double'),
    'string_' : ('com.illumon.iris.db.v2.sources.immutable.ImmutableObjectArraySource', 'java.lang.String'),
    'datetime64[ns]': ('com.illumon.iris.db.v2.sources.immutable.ImmutableDateTimeArraySource', 'long')}


