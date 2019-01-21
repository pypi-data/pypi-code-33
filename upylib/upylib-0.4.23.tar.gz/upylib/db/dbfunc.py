from __future__ import print_function
import sqlite3
import os


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def db_connect(db_fn, verbosity=1):
    try:
        db = sqlite3.connect(db_fn)
        db.text_factory = str
        db.row_factory = sqlite3.Row
        return db
    except Exception as e:
        if verbosity >= 1:
            print("connect_db exception: %s" % e)
        return False


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def db_recreate(db_fn, verbosity=1):
    try:
        if os.path.isfile(db_fn):
            os.remove(db_fn)
        return db_connect(db_fn)
    except Exception as e:
        if verbosity >= 1:
            print("db_recreate_table exception: %s" % e)
        return False


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def db_get_table_names(db_fn, verbosity=1):
    sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    res = db_select_query(db_fn, sql)
    tmplist = list()
    for row in res:
        tmplist.append(row[0])
    return tmplist

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def db_get_column_names(db_fn, table_name, verbosity=1):
    db = db_connect(db_fn)
    try:
        cur = db.cursor()
        columns = [i[1] for i in cur.execute("PRAGMA table_info(%s)"%table_name)]
    except Exception as e:
        if verbosity >= 1:
            print("db_create_table exception: %s" % e)
        return False
    return columns

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def db_assert_column(db_fn, table_name, column_name, opt, verbosity=1):
    columns = db_get_column_names(db_fn, table_name)
    if not columns:
        return False

    if column_name in columns:
        return True
    else:
        q = "ALTER TABLE %s ADD COLUMN %s %s" % (table_name, column_name, opt)
        return db_execute_query(db_fn, q)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def db_execute_query(db_fn, sql, verbosity=1):
    db = db_connect(db_fn)
    try:
        cur = db.cursor()
        cur.execute(sql)
    except Exception as e:
        if verbosity >= 1:
            print("db_execute_query exception: %s" % e)
        return False
    return True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def db_create_table(db_fn, sql, verbosity=1):
    return db_execute_query(db_fn, sql, verbosity)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def db_drop_table(db_fn, tbl_name, verbosity=1):
    sql="DROP TABLE IF EXISTS %s" % tbl_name
    return db_execute_query(db_fn, sql, verbosity)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def db_insert_query(db_fn, sql, data, verbosity=1):
    try:
        db = db_connect(db_fn)
        cur = db.cursor()
        cur.execute(sql, data)
        db.commit()
        i = cur.lastrowid

    except Exception as e:
        print("db_insert_query exception: %s" % e)
        return False

    return i


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def db_insert_query_many(db_fn, sql, data_list, verbosity=1):
    try:
        db = db_connect(db_fn)
        cur = db.cursor()
        cur.executemany(sql, data_list)
        db.commit()
        i = cur.lastrowid

    except Exception as e:
        if verbosity >= 1:
           print("db_insert_query_many exception: %s" % e)
        return False

    return i


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def db_select_query(db_fn, sql, verbosity=1):
    try:
        db = db_connect(db_fn)
        cur = db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

    except Exception as e:
        if verbosity >= 1:
            print( "db_select_query exception: %s" % e)
            return False

    return rows


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def db_delete_query(db_fn, sql, verbosity=1):
    try:
        db = db_connect(db_fn)
        cur = db.cursor()
        cur.execute(sql)
        db.commit()

    except Exception as e:
        if verbosity >= 1:
            print( "db_delete_query exception: %s" % e)
            return False

    return True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def db_update_query(db_fn, sql, verbosity=1):
    try:
        db = db_connect(db_fn)
        cur = db.cursor()
        cur.execute(sql)
        db.commit()

    except Exception as e:
        if verbosity >= 1:
            print( "db_update_query exception: %s" % e)
            return False

    return True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def db_is_table(db_fn, tbl_name, verbosity=1):
    db = db_connect(db_fn)
    sql = """
        SELECT name FROM sqlite_master WHERE type='table' and name='%s'
    """ % tbl_name
    res = db_select_query(db, sql, verbosity)
    if len(res) == 0:
        return False
    return True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def run():
    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
if __name__ == "__main__":
    run()
