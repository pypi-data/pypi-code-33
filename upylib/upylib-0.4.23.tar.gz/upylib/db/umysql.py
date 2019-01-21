from __future__ import print_function

import sys
import MySQLdb

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
if sys.version_info < (3, 0, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
class UMySQL:
    verbose = 1

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    def __init__(self, db_host, db_user, db_passwd, db_name):
        self.connect(db_host, db_user, db_passwd, db_name )

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    def connect(self, db_host, db_user, db_passwd, db_name):
        self.db = MySQLdb.connect(db_host, db_user, db_passwd, db_name, charset="utf8")
        if self.db:
            return True
        else:
            return False

    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    def get_table_names(self):
        return db_get_table_names(self.db_fn)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    def get_column_names(self, table_name):
        return db_get_column_names(self.db_fn, table_name)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    def assert_column(self, table_name, column_name, opt):
        return db_assert_column(self.db_fn, table_name, column_name, opt)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    def is_table(self, tbl_name, verbosity=1):
        return db_is_table(self.db_fn, tbl_name, verbosity)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    def create_table(self, sql, verbosity=1):
        return db_create_table(self.db_fn, sql, verbosity)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    def drop_table(self, tbl_name, verbosity=1):
        return db_drop_table(self.db_fn, tbl_name, verbosity)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    def delete_query(self, sql, verbosity=1):
        return db_delete_query(self.db_fn, sql, verbosity)
    """

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    def select_query(self, sql, verbosity=1):
        if not self.db:
            return False

        with self.db.cursor() as cur:
            cur.execute(sql)
            res = cur.fetchall()
            return res

    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    def update_query(self, sql, verbosity=1):
        return db_update_query(self.db_fn, sql, verbosity)
    """

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    def insert_query(self, sql, data, verbosity=1):
        if not self.db:
            return False

        cur = self.db.cursor()
        print(cur)
        print(sql)
        print(data)
        cur.execute(sql, data)
        self.db.commit()

        return True

    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    def insert_query_many(self, sql, data_list, verbosity=1):
        return db_insert_query_many(self.db_fn, sql, data_list, verbosity)
    """


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("usage: %s" % (sys.argv[0]))
        sys.exit()
