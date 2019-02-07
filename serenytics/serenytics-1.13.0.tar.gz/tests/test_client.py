import datetime
from uuid import uuid4

import pytest


class TestClient(object):

    @pytest.fixture(autouse=True)
    def setup(self, serenytics_client, storage_data_source):
        self._client = serenytics_client
        self._data_source = storage_data_source

    def test_get_or_create_storage_data_source_by_name(self):
        data_source = self._client.get_or_create_storage_data_source_by_name(self._data_source.name)
        assert data_source._config == self._data_source._config

        # check filtering by name actually works on GET /api/data_source
        new_data_source_name = 'test_' + str(uuid4())
        data_source = self._client.get_or_create_storage_data_source_by_name(new_data_source_name)
        assert data_source.name == new_data_source_name

    def test_get_data_source_by_uuid(self):
        data_source = self._client.get_data_source_by_uuid(self._data_source.uuid)
        assert data_source._config == self._data_source._config

    def test_get_data_source_by_name(self):
        data_source = self._client.get_data_source_by_name(self._data_source.name)
        assert data_source._config == self._data_source._config

    def test_storage(self):
        data = {'last_execution_time': datetime.datetime.utcnow()}
        self._client.store_script_data(data)
        assert self._client.retrieve_script_data() == data
