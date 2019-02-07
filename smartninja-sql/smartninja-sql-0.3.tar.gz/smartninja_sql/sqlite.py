import sqlite3

from prettytable import PrettyTable


class SQLiteDatabase:
    def __init__(self, name=":memory:"):
        try:
            self.conn = sqlite3.connect(name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(e)

    def execute(self, *args, **kwargs):
        """
        Example: db.execute(SELECT * FROM User)
        :param args:
        :param kwargs:
        :return:
        """
        try:
            query = self.cursor.execute(*args, **kwargs)
            self.conn.commit()
            return query.fetchall()
        except sqlite3.Error as e:
            print(e)
            return None

    def pretty_print(self, *args, **kwargs):
        """
        Example: db.pretty_print(SELECT * FROM User)
        :param args:
        :param kwargs:
        :return:
        """
        try:
            query = self.cursor.execute(*args, **kwargs)
            self.conn.commit()
            rows = query.fetchall()

            field_names = query.description

            table = PrettyTable(field_names=[header[0] for header in field_names])

            for row in rows:
                table.add_row(row)

            print(table)

            return rows
        except sqlite3.Error as e:
            print(e)
            return None

    def print_tables(self, verbose=False):
        tables = self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()

        if verbose:
            for table in tables:
                if table[0] != "sqlite_sequence":
                    print("{table_name}:".format(table_name=table[0]))
                    fields = self.cursor.execute("PRAGMA table_info('%s');" % table[0]).fetchall()
                    for field in fields:
                        print("- {field_name} ({field_type})".format(field_name=field[1], field_type=field[2]))
                    print("")
        else:
            for table in tables:
                if table[0] != "sqlite_sequence":
                    print(table[0])

    def close(self):
        self.cursor.close()
        self.conn.close()
