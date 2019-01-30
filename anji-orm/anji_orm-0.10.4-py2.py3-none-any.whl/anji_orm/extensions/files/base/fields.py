import typing

from anji_orm import Field, orm_register
from anji_orm.core.context import CONTEXT_MARKS
from anji_orm.core.fields.base import DICT_ORIGIN

from .data_model import FileRecord, FileDictProxy

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.4"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

FILE_FIELD_MARK = 'extensions_file_field_mark'
FILE_DICT_FIELD_MARK = 'extensions_file_dict_field_mark'


class FileField(Field):

    __slots__ = ('old_values', 'value_changed')

    old_values: typing.Dict[int, typing.List[FileRecord]]
    value_changed: typing.Dict[int, bool]

    _anji_orm_extension: str = 'file'

    def __init__(self, **kwargs) -> None:
        field_marks = kwargs.pop('field_marks', [])
        field_marks.append(FILE_FIELD_MARK)
        super().__init__(**kwargs, field_marks=field_marks)  # type: ignore
        self.old_values = {}
        self.value_changed = {}

    def real_value(self, model_record):
        file = model_record._values.get(self.name)
        if isinstance(file, FileRecord):
            return {
                'name': file.name,
                'in_bytes': file.in_bytes
            }
        return {
            'name': file,
            'in_bytes': False
        }

    def can_be(self, target_type: typing.Type) -> bool:
        if hasattr(target_type, '__origin__') and target_type.__origin__ is not None:
            if target_type.__origin__ is DICT_ORIGIN and target_type.__args__:
                return False
            target_type = target_type.__origin__
        if issubclass(dict, target_type):
            return True
        return super().can_be(target_type)

    def __get__(self, instance, instance_type):
        if instance is None:
            raise TypeError("You can't use this field to build query!")
        file = instance._values.get(self.name)
        return file

    def __set__(self, instance, value) -> None:
        if isinstance(value, dict):
            value = FileRecord(value['name'], record=instance, in_bytes=value['in_bytes'])
        elif isinstance(value, FileRecord):
            value._record = instance
        old_value = instance._values.get(self.name)
        super().__set__(instance, value)
        if isinstance(old_value, FileRecord):
            if id(instance) not in self.old_values:
                self.old_values[id(instance)] = []
            self.old_values[id(instance)].append(old_value)
        if not getattr(CONTEXT_MARKS, 'load', False):
            self.value_changed[id(instance)] = True


class FileDictField(Field):

    __slots__ = ('old_values', 'value_changed')

    _anji_orm_extension: str = 'file'

    old_values: typing.Dict[int, typing.List[FileDictProxy]]
    value_changed: typing.Dict[int, bool]

    def __init__(self, **kwargs) -> None:
        field_marks = kwargs.pop('field_marks', [])
        field_marks.append(FILE_DICT_FIELD_MARK)
        super().__init__(**kwargs, field_marks=field_marks)  # type: ignore
        self.old_values = {}
        self.value_changed = {}

    def real_value(self, model_record):
        file_dict_proxy = model_record._values.get(self.name)
        if file_dict_proxy is None:
            return None
        return {
            file_name: {
                'name': file.name,
                'in_bytes': file.in_bytes
            } for file_name, file in file_dict_proxy.items()
        }

    def can_be(self, target_type: typing.Type) -> bool:
        if hasattr(target_type, '__origin__') and target_type.__origin__ is DICT_ORIGIN:
            return target_type.__args__ == (str, FileRecord)
        if hasattr(target_type, '__origin__') and target_type.__origin__ is not None:
            target_type = target_type.__origin__
        if issubclass(dict, target_type):
            return True
        return super().can_be(target_type)

    def __get__(self, instance, instance_type):
        if instance is None:
            raise TypeError("You can't use this field to build query!")
        file = instance._values.get(self.name)
        return file

    def __set__(self, instance, value) -> None:
        if isinstance(value, dict):
            value = FileDictProxy.from_dict(value, instance)
        elif isinstance(value, FileDictProxy):
            raise ValueError("Please, set dict instead of FileDictProxy!")
        old_value = instance._values.get(self.name)
        if value is not None and not isinstance(value, FileDictProxy):
            raise ValueError(f'Field {self.name} value should have dict` type instead of {value}')
        instance._values[self.name] = orm_register.backend_adapter.ensure_compatibility(value)
        if isinstance(old_value, FileDictProxy):
            if id(instance) not in self.old_values:
                self.old_values[id(instance)] = []
            self.old_values[id(instance)].append(old_value)
        if not getattr(CONTEXT_MARKS, 'load', False):
            self.value_changed[id(instance)] = True
