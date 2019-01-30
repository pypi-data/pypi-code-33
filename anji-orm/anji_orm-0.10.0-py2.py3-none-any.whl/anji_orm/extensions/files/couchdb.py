from anji_orm import core, orm_register
from anji_orm.couchdb.utils import CouchDBRequestException

from .base import AbstractFileExtension, FileRecord
from ..exceptions import UnsupportedExtensionConfiguration, RecordBindException

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.0"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['CouchDBFileExtension']


class CouchDBFileExtension(AbstractFileExtension):

    __slots__ = ()

    @staticmethod
    def _build_upload_file_query(record: core.Model, file_record: FileRecord):
        params = {}
        if '_rev' in record._meta:
            params['rev'] = record._meta['_rev']
        return {
            "method": "put",
            "url": f"/{record._table}/{record.id}/{file_record.name}",
            "data": file_record.content,
            "params": params
        }

    @staticmethod
    def _build_download_file_query(record: core.Model, name: str):
        return {
            "method": "get",
            "url": f"/{record._table}/{record.id}/{name}"
        }

    @staticmethod
    def _build_delete_file_query(record: core.Model, name: str):
        params = {}
        if '_rev' in record._meta:
            params['rev'] = record._meta['_rev']
        return {
            "method": "delete",
            "url": f"/{record._table}/{record.id}/{name}",
            "params": params
        }

    def upload_file(self, file_record: FileRecord) -> None:
        if file_record.record is None:
            raise RecordBindException('For this operation, file_record should be bind to record')
        response = orm_register.sync_strategy.execute_query(self._build_upload_file_query(file_record.record, file_record))
        file_record.record._meta['_rev'] = response['rev']

    async def async_upload_file(self, file_record: FileRecord) -> None:
        if file_record.record is None:
            raise RecordBindException('For this operation, file_record should be bind to record')
        response = await orm_register.async_strategy.execute_query(self._build_upload_file_query(file_record.record, file_record))
        file_record.record._meta['_rev'] = response['rev']

    def download_file(self, file_record: FileRecord) -> None:
        if file_record.record is None:
            raise RecordBindException('For this operation, file_record should be bind to record')
        file_content = orm_register.sync_strategy.execute_query(
            self._build_download_file_query(file_record.record, file_record.name)
        )
        if not file_record.in_bytes and isinstance(file_content, bytes):
            file_content = file_content.decode('utf-8')
        file_record._content = file_content

    async def async_download_file(self, file_record: FileRecord) -> None:
        if file_record.record is None:
            raise RecordBindException('For this operation, file_record should be bind to record')
        file_content = await orm_register.async_strategy.execute_query(
            self._build_download_file_query(file_record.record, file_record.name)
        )
        if not file_record.in_bytes and isinstance(file_content, bytes):
            file_content = file_content.decode('utf-8')
        file_record._content = file_content

    async def async_delete_file(self, file_record: FileRecord) -> None:
        try:
            if file_record.record is None:
                raise RecordBindException('For this operation, file_record should be bind to record')
            response = await orm_register.async_strategy.execute_query(self._build_delete_file_query(file_record.record, file_record.name))
            file_record.record._meta['_rev'] = response['rev']
        except CouchDBRequestException as exc:
            if exc.status_code != 404:
                raise

    def delete_file(self, file_record: FileRecord) -> None:
        try:
            if file_record.record is None:
                raise RecordBindException('For this operation, file_record should be bind to record')
            response = orm_register.sync_strategy.execute_query(self._build_delete_file_query(file_record.record, file_record.name))
            file_record.record._meta['_rev'] = response['rev']
        except CouchDBRequestException as exc:
            if exc.status_code != 404:
                raise

    async def async_load(self):
        await super().async_load()
        if orm_register.selected_protocol != core.RegistryProtocol.couchdb:
            raise UnsupportedExtensionConfiguration('You can use couchdb file extension only with couchdb database')

    def load(self):
        super().load()
        if orm_register.selected_protocol != core.RegistryProtocol.couchdb:
            raise UnsupportedExtensionConfiguration('You can use couchdb file extension only with couchdb database')
