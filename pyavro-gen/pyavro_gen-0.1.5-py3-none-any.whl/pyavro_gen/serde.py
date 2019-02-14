"""
This module is added as __init__.py of the main packages of generated classes.

It patches fastavro enum reader and writer to take enums as input (and return as output)
instead of strings.

Since it cannot know which enum class to return, we keep a dictionary of enum classes
found in the package and match them with the fully qualified domain of the avro schema,
during deserialization.
"""

import enum
import glob
import inspect
from importlib import import_module
from pathlib import Path
from typing import Dict

import confluent_kafka.avro.serializer
import fastavro._read_py as fastavro_read  # pylint: disable=W0212
import fastavro._validation_py as fastavro_validation  # pylint: disable=W0212
import fastavro._write_py as fastavro_write  # pylint: disable=W0212
from fastavro._read_common import SchemaResolutionError  # pylint: disable=W0212
from fastavro._read_py import read_long  # pylint: disable=W0212
from fastavro._write_py import write_int  # pylint: disable=W0212

ENUM_CLASSES: Dict[str, type] = {}

RESOLVED_NAMESPACE = Path(__file__).parent.resolve()
PACKAGE = RESOLVED_NAMESPACE.name.replace('/', '')
ROOT_DIR = str(RESOLVED_NAMESPACE.parent)
if not ROOT_DIR.endswith('/'):
    ROOT_DIR += '/'

for file in glob.iglob(str(RESOLVED_NAMESPACE) + '/**/__init__.py', recursive=True):
    module_name = str(Path(file).parent).replace(ROOT_DIR, '').replace('/', '.')
    module = import_module(module_name, PACKAGE)
    for _, class_type in inspect.getmembers(module, inspect.isclass):
        if issubclass(class_type, enum.Enum):
            # Here we remove the base package.
            # Also, class module name is snake case, but classes are imported
            # in their packages' __init__.py so classes' module names have to be removed.
            # e.g.
            # from   'avroclasses.com.jaumo.schema.domain.user.gender.Gender'
            # to     'com.jaumo.schema.domain.user.Gender'
            class_module = class_type.__module__
            class_module_no_package = class_module[class_module.find('.') + 1:]
            parent_class_module_no_package = \
                class_module_no_package[:class_module_no_package.rfind('.') + 1]
            fully_qualified_name = parent_class_module_no_package + class_type.__name__

            ENUM_CLASSES[fully_qualified_name] = class_type
for k, v in ENUM_CLASSES.items():
    print(k, v)


# pylint: disable=W0613
def my_validate_enum(datum, schema, **kwargs):  # type: ignore
    """
    Check that the data value matches one of the enum symbols.

    i.e "blue" in ["red", green", "blue"]

    Parameters
    ----------
    datum: Any
        Data being validated
    schema: dict
        Schema
    kwargs: Any
        Unused kwargs
    """
    return datum.value in schema['symbols']


# pylint: disable=C0103
def my_write_enum(fo, datum, schema):  # type: ignore
    """An enum is encoded by a int, representing the zero-based position of
    the symbol in the schema."""
    index = schema['symbols'].index(datum.value)
    write_int(fo, index)


# pylint: disable=C0103
def my_read_enum(fo, writer_schema, reader_schema=None):  # type: ignore
    """An enum is encoded by a int, representing the zero-based position of the
    symbol in the schema.
    """
    index = read_long(fo)
    symbol = writer_schema['symbols'][index]
    if reader_schema and symbol not in reader_schema['symbols']:
        default = reader_schema.get("default")
        if default:
            return default

        symlist = reader_schema['symbols']
        msg = '%s not found in reader symbol list %s' % (symbol, symlist)
        raise SchemaResolutionError(msg)

    klass_fully_qualified_name = writer_schema['name']
    klass = ENUM_CLASSES[klass_fully_qualified_name]
    return klass(symbol)


fastavro_validation.VALIDATORS['enum'] = my_validate_enum
fastavro_write.WRITERS['enum'] = my_write_enum
fastavro_write.validate = fastavro_validation.validate
fastavro_read.READERS['enum'] = my_read_enum

confluent_kafka.avro.serializer.schemaless_writer = fastavro_write.schemaless_writer
confluent_kafka.avro.serializer.schemaless_reader = fastavro_read.schemaless_reader
