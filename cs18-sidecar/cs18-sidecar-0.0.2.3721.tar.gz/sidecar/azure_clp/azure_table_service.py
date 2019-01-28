import json
from typing import List

from azure.cosmosdb.table import Entity
from azure.cosmosdb.table.tableservice import TableService

from sidecar.azure_clp.data_store_service import DataStoreService


class AzureTableService(DataStoreService):

    def __init__(self, table_service: TableService,
                 table_name: str = "colonySandboxes",
                 default_partition_key: str = "colonySandbox"):
        super().__init__()
        self.default_partition_key = default_partition_key
        self.table_service = table_service
        self.table_name = table_name

        # create the table if not exists
        self.table_service.create_table(table_name=self.table_name,
                                        fail_on_exist=False)

    def find_data_by_id(self, data_id: str) -> dict:
        entity = self.table_service.get_entity(table_name=self.table_name,
                                               row_key=data_id,
                                               partition_key=self.default_partition_key)
        res = self._convert_entity_to_dict(entity)
        return res

    def update_data(self, data_id: str, data: dict, column_name: str):
        entity = self._to_entity(data={column_name: data},
                                 data_id=data_id)

        self.table_service.merge_entity(table_name=self.table_name,
                                        entity=entity)

    def _to_entity(self, data: dict, data_id: str):
        task = Entity()
        task.PartitionKey = self.default_partition_key
        task.RowKey = str(data_id)
        for k, v in data.items():
            task[str(k).replace("-", "__")] = str(v)
        return task

    def _convert_entity_to_dict(self, entity):
        res = {}
        table_infra_keys = {'PartitionKey', "RowKey", "Timestamp", "etag"}
        for k, v in entity.items():
            key = str(str(k).replace("__", "-"))
            if key not in table_infra_keys:
                res[key] = json.loads(json.dumps(str(v)))
        return res
