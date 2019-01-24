import abc
from typing import List


class DataStoreService(metaclass=abc.ABCMeta):

    def __init__(self):
        pass

    def insert_data(self, data: dict, data_id: str):
        pass

    def find_data_by_id(self, data_id: str) -> dict:
        pass

    def find_data_by_ids(self, id_column_name: str, ids: List[str]) -> List[dict]:
        pass

    def delete_data_by_id(self, data_id: str) -> bool:
        pass

    def update_data(self, data_id: str, data: str, column_name: str):
        pass
