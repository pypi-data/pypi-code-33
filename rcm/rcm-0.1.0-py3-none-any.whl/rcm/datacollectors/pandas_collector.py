from mesa.datacollection import DataCollector
import pandas as pd


class PandasCollector(DataCollector):
    def __init__(self, **kwargs):
        self._table_descriptions = {}

        super().__init__(**kwargs)

    def _new_table(self, table_name, table_description):
        """ Add a new table that objects can write to.

        Args:
            table_name: Name of the new table.
            table_description: Dictionary with index and columns to add to the table.

        """
        self._table_descriptions[table_name] = table_description

        new_table = pd.DataFrame(columns=table_description['columns'])
        if 'index' in table_description:
            new_table = new_table.set_index(table_description['index'])
        self.tables[table_name] = new_table

    def add_table_row(self, table_name, row, columns=None):
        """ Add a row dictionary to a specific table.

        Args:
            table_name: Name of the table to append a row to.
            row: A dictionary of the form {column_name: value...}
            ignore_missing: If True, fill any missing columns with Nones;
                            if False, throw an error if any columns are missing

        """
        if table_name not in self.tables:
            raise Exception("Table does not exist.")

        table_description = self._table_descriptions[table_name]

        if columns is None:
            columns = table_description['columns']
        elif not set(columns).issubset(set(table_description['columns'])):
            raise Exception("Supplied columns are not a subset of the tables columns")

        new_row = pd.DataFrame([row], columns=columns)
        if 'index' in table_description:
            new_row = new_row.set_index(table_description['index'])

        new_df = self.tables[table_name].append(new_row, sort=False)

        self.tables[table_name] = new_df

    def update_table_row(self, table_name, index, values, columns=None):
        if table_name not in self.tables:
            raise Exception("No such table: "+table_name)

        table = self.tables[table_name]
        if index not in table.index:
            raise Exception("No such index in table: "+str(index))

        if columns is None:
            columns = self._table_descriptions[table_name]['columns']

        for column in columns:
            table.loc[index][column] = values[column]

    def get_table_dataframe(self, table_name):
        """ Create a pandas DataFrame from a particular table.

        Args:
            table_name: The name of the table to convert.

        """
        if table_name not in self.tables:
            raise Exception("No such table.")
        return self.tables[table_name].copy(deep=True)
