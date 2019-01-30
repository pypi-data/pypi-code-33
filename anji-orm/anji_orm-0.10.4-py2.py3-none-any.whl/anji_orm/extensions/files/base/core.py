import abc
import typing

import aenum
from anji_orm import orm_register, extensions, core
from anji_orm.core.model import FIELD_CLASS_SELECTION_HOOK, Model
from anji_orm.core.fields.base import DICT_ORIGIN

from .data_model import FileRecord, FileDictProxy
from .fields import (
    FileField, FileDictField,
    FILE_FIELD_MARK, FILE_DICT_FIELD_MARK
)

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.4"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['FileExtensionProtocol', 'AbstractFileExtension']


def file_field_selection_listener(attr, attr_type) -> typing.Optional[FileField]:
    if attr_type is FileRecord:
        return FileField(default=attr)
    return None


def file_dict_field_selection_listener(attr, attr_type) -> typing.Optional[FileDictField]:  # pylint: disable=invalid-name
    if hasattr(attr_type, '__origin__') and attr_type.__origin__ is DICT_ORIGIN and attr_type.__args__[1] is FileRecord:
        return FileDictField(default=attr)
    return None


FIELD_CLASS_SELECTION_HOOK.subscribe(file_field_selection_listener)
FIELD_CLASS_SELECTION_HOOK.subscribe(file_dict_field_selection_listener)


class FileExtensionProtocol(aenum.Enum):

    couchdb = 'anji_orm.extensions.files.couchdb.CouchDBFileExtension'
    disk = 'anji_orm.extensions.files.disk.DiskFileExtension'


class AbstractFileExtension(extensions.BaseExtension):

    __slots__ = ()

    @staticmethod
    def _unqlite_serialize_file_record(value: typing.Dict):
        if value is not None and 'name' in value and value['name'] is not None:
            value['name'] = value['name'].encode('utf-8')
        return value

    @staticmethod
    def _unqlite_deserialize_file_record(value: typing.Dict, _result_type):
        if value is not None and 'name' in value and value['name'] is not None:
            value['name'] = value['name'].decode('utf-8')
        return value

    @staticmethod
    def _unqlite_serialize_file_dict(value: typing.Dict):
        if value is not None:
            for key in value:
                value[key] = AbstractFileExtension._unqlite_serialize_file_record(value[key])
        return value

    @staticmethod
    def _unqlite_deserialize_file_dict(value: typing.Dict, _result_type):
        if value is not None:
            for key in value:
                value[key] = AbstractFileExtension._unqlite_deserialize_file_record(value[key], None)
        return value

    @staticmethod
    def update_adapter():
        if orm_register.selected_protocol == core.RegistryProtocol.unqlite:
            orm_register.backend_adapter.register_deserialization(
                FileRecord, AbstractFileExtension._unqlite_deserialize_file_record
            )
            orm_register.backend_adapter.register_serialization(
                FileRecord, AbstractFileExtension._unqlite_serialize_file_record
            )
            orm_register.backend_adapter.register_deserialization(
                typing.Dict[str, FileRecord], AbstractFileExtension._unqlite_deserialize_file_dict
            )
            orm_register.backend_adapter.register_serialization(
                typing.Dict[str, FileRecord], AbstractFileExtension._unqlite_serialize_file_dict
            )

    @staticmethod
    def update_listeners():
        Model.async_send.after.subscribe(AbstractFileExtension.async_model_send_handler)  # pylint: disable=no-member
        Model.send.after.subscribe(AbstractFileExtension.sync_model_send_handler)  # pylint: disable=no-member

    async def async_load(self):
        self.update_adapter()
        self.update_listeners()

    def load(self):
        self.update_adapter()
        self.update_listeners()

    @abc.abstractmethod
    def upload_file(self, file_record: FileRecord) -> None:
        pass

    @abc.abstractmethod
    async def async_upload_file(self, file_record: FileRecord) -> None:
        pass

    @abc.abstractmethod
    def download_file(self, file_record: FileRecord) -> None:
        pass

    @abc.abstractmethod
    async def async_download_file(self, file_record: FileRecord) -> None:
        pass

    @abc.abstractmethod
    async def async_delete_file(self, file_record: FileRecord) -> None:
        pass

    @abc.abstractmethod
    def delete_file(self, file_record: FileRecord) -> None:
        pass

    @classmethod
    async def async_process_file_field_logic(cls, record: Model, record_python_id: int) -> None:
        for field_name in record._field_marks.get(FILE_FIELD_MARK, []):
            field: FileField = record._fields.get(field_name)  # type: ignore
            actual_value: FileRecord = getattr(record, field_name)
            if field.value_changed.get(record_python_id, False):
                # cleanup old values
                if record_python_id in field.old_values:
                    for old_value in field.old_values[record_python_id]:
                        await orm_register.shared.file_extension.async_delete_file(old_value)
                    del field.old_values[record_python_id]
                # upload new value
                if actual_value is not None:
                    await orm_register.shared.file_extension.async_upload_file(actual_value)
                del field.value_changed[record_python_id]
            else:
                if actual_value is not None and actual_value.changed:
                    await orm_register.shared.file_extension.async_upload_file(actual_value)
                    actual_value.reset()

    @classmethod
    async def async_process_file_dict_field_logic(cls, record: Model, record_python_id: int) -> None:  # pylint: disable=invalid-name,too-many-branches
        for field_name in record._field_marks.get(FILE_DICT_FIELD_MARK, []):
            field: FileDictField = record._fields.get(field_name)  # type: ignore
            actual_value: FileDictProxy = getattr(record, field_name)
            if field.value_changed.get(record_python_id, False):
                # cleanup old values
                if record_python_id in field.old_values:
                    for old_dict_value in field.old_values[record_python_id]:
                        for old_value in old_dict_value.values():
                            await orm_register.shared.file_extension.async_delete_file(old_value)
                    del field.old_values[record_python_id]
                # upload new value
                if actual_value is not None:
                    for new_file in actual_value.values():
                        await orm_register.shared.file_extension.async_upload_file(new_file)
                    actual_value.changed_keys.clear()
                del field.value_changed[record_python_id]
            else:
                if actual_value is not None and actual_value.changed:
                    for changed_key in actual_value.changed_keys:
                        if changed_key in actual_value:
                            file = actual_value[changed_key]
                            await orm_register.shared.file_extension.async_upload_file(file)
                            file.reset()
                    for old_file in actual_value.old_values:
                        await orm_register.shared.file_extension.async_delete_file(old_file)
                    for file_name, file in actual_value.items():
                        if file.changed and file_name not in actual_value.changed_keys:
                            await orm_register.shared.file_extension.async_upload_file(file)
                            file.reset()
                    actual_value.changed_keys.clear()
                    actual_value.old_values.clear()

    @classmethod
    def process_file_field_logic(cls, record: Model, record_python_id: int) -> None:
        for field_name in record._field_marks.get(FILE_FIELD_MARK, []):
            field: FileField = record._fields.get(field_name)  # type: ignore
            actual_value: FileRecord = getattr(record, field_name)
            if field.value_changed.get(record_python_id, False):
                # cleanup old values
                if record_python_id in field.old_values:
                    for old_value in field.old_values[record_python_id]:
                        orm_register.shared.file_extension.delete_file(old_value)
                    del field.old_values[record_python_id]
                # upload new value
                if actual_value is not None:
                    orm_register.shared.file_extension.upload_file(actual_value)
                del field.value_changed[record_python_id]
            else:
                if actual_value is not None and actual_value.changed:
                    orm_register.shared.file_extension.upload_file(actual_value)
                    actual_value.reset()

    @classmethod
    def process_file_dict_field_logic(cls, record: Model, record_python_id: int) -> None:  # pylint: disable=too-many-branches
        for field_name in record._field_marks.get(FILE_DICT_FIELD_MARK, []):
            field: FileDictField = record._fields.get(field_name)  # type: ignore
            actual_value: FileDictProxy = getattr(record, field_name)
            if field.value_changed.get(record_python_id, False):
                # cleanup old values
                if record_python_id in field.old_values:
                    for old_dict_value in field.old_values[record_python_id]:
                        for old_value in old_dict_value.values():
                            orm_register.shared.file_extension.delete_file(old_value)
                    del field.old_values[record_python_id]
                # upload new value
                if actual_value is not None:
                    for new_file in actual_value.values():
                        orm_register.shared.file_extension.upload_file(new_file)
                del field.value_changed[record_python_id]
            else:
                if actual_value is not None and actual_value.changed:
                    for changed_key in actual_value.changed_keys:
                        if changed_key in actual_value:
                            file = actual_value[changed_key]
                            orm_register.shared.file_extension.upload_file(file)
                            file.reset()
                    for old_file in actual_value.old_values:
                        orm_register.shared.file_extension.delete_file(old_file)
                    for file_name, file in actual_value.items():
                        if file.changed and file_name not in actual_value.changed_keys:
                            orm_register.shared.file_extension.upload_file(file)
                            file.reset()
                    actual_value.changed_keys.clear()
                    actual_value.old_values.clear()

    @classmethod
    async def async_model_send_handler(cls, record: Model) -> None:
        if 'file' in record._used_extensions:  # type: ignore
            record_python_id = id(record)
            await cls.async_process_file_field_logic(record, record_python_id)
            await cls.async_process_file_dict_field_logic(record, record_python_id)

    @classmethod
    def sync_model_send_handler(cls, record: Model) -> None:
        if 'file' in record._used_extensions:  # type: ignore
            record_python_id = id(record)
            cls.process_file_field_logic(record, record_python_id)
            cls.process_file_dict_field_logic(record, record_python_id)
