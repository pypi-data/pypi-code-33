from abc import abstractmethod
from tmg_etl_library.components.component import Component


class Database(Component):
    def __init__(self, log):
        super().__init__(log)

    @abstractmethod
    def table_exists(self, table):
        pass

    @abstractmethod
    def create_table(self, table):
        pass

    @abstractmethod
    def delete_tables(self, tables):
        pass

    @abstractmethod
    def run_query(self, destination, use_legacy_sql, destination_config):
        pass
