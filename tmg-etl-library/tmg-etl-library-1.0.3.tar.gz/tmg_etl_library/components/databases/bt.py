from tmg_etl_library.components.databases.database import Database


class BTClient(Database):
    def __init__(self, log):
        super().__init__(log)

    def get_schema(self):
        pass

    def table_exists(self):
        pass

    def delete_tables(self):
        pass

    def create_table(self, table):
        pass

    def insert_data(self):
        pass

    def run_query(self):
        pass


class BTTable:
    pass
