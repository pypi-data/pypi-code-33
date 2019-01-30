import os
import urllib.parse

import aiofiles

from .base import AbstractFileExtension, FileRecord
from ..exceptions import RecordBindException

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['DiskFileExtension']


class DiskFileExtension(AbstractFileExtension):

    __slots__ = ('base_path', )

    def __init__(self, uri: str) -> None:
        super().__init__(uri)
        self.base_path = urllib.parse.urlparse(uri).path

    @staticmethod
    def _ensure_directory(path) -> None:
        if not os.path.exists(path):
            os.mkdir(path)

    async def async_load(self):
        await super().async_load()
        self._ensure_directory(self.base_path)

    def load(self):
        super().load()
        self._ensure_directory(self.base_path)

    def upload_file(self, file_record: FileRecord) -> None:
        if file_record.record is None:
            raise RecordBindException('For this operation, file_record should be bind to record')
        table_path = os.path.join(self.base_path, file_record.record._table)
        record_path = os.path.join(table_path, file_record.record.id)  # type: ignore
        self._ensure_directory(table_path)
        self._ensure_directory(record_path)
        open_mode = 'wb' if file_record.in_bytes else 'w'
        with open(os.path.join(record_path, file_record.name), mode=open_mode) as target_file:  # type: ignore
            target_file.write(file_record.content)

    async def async_upload_file(self, file_record: FileRecord) -> None:
        if file_record.record is None:
            raise RecordBindException('For this operation, file_record should be bind to record')
        table_path = os.path.join(self.base_path, file_record.record._table)
        record_path = os.path.join(table_path, file_record.record.id)  # type: ignore
        self._ensure_directory(table_path)
        self._ensure_directory(record_path)
        open_mode = 'wb' if file_record.in_bytes else 'w'
        async with aiofiles.open(os.path.join(record_path, file_record.name), mode=open_mode) as target_file:  # type: ignore
            await target_file.write(file_record.content)

    def download_file(self, file_record: FileRecord) -> None:
        if file_record.record is None:
            raise RecordBindException('For this operation, file_record should be bind to record')
        table_path = os.path.join(self.base_path, file_record.record._table)
        record_path = os.path.join(table_path, file_record.record.id)  # type: ignore
        self._ensure_directory(table_path)
        self._ensure_directory(record_path)
        open_mode = 'rb' if file_record.in_bytes else 'r'
        with open(os.path.join(record_path, file_record.name), mode=open_mode) as target_file:
            file_record.content = target_file.read()

    async def async_download_file(self, file_record: FileRecord) -> None:
        if file_record.record is None:
            raise RecordBindException('For this operation, file_record should be bind to record')
        table_path = os.path.join(self.base_path, file_record.record._table)
        record_path = os.path.join(table_path, file_record.record.id)  # type: ignore
        self._ensure_directory(table_path)
        self._ensure_directory(record_path)
        open_mode = 'rb' if file_record.in_bytes else 'r'
        async with aiofiles.open(os.path.join(record_path, file_record.name), mode=open_mode) as target_file:
            file_record.content = await target_file.read()

    async def async_delete_file(self, file_record: FileRecord) -> None:
        if file_record.record is None:
            raise RecordBindException('For this operation, file_record should be bind to record')
        table_path = os.path.join(self.base_path, file_record.record._table)
        record_path = os.path.join(table_path, file_record.record.id)  # type: ignore
        self._ensure_directory(table_path)
        self._ensure_directory(record_path)
        os.remove(os.path.join(record_path, file_record.name))

    def delete_file(self, file_record: FileRecord) -> None:
        if file_record.record is None:
            raise RecordBindException('For this operation, file_record should be bind to record')
        table_path = os.path.join(self.base_path, file_record.record._table)
        record_path = os.path.join(table_path, file_record.record.id)  # type: ignore
        self._ensure_directory(table_path)
        self._ensure_directory(record_path)
        os.remove(os.path.join(record_path, file_record.name))
