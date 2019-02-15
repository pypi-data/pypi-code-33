import psycopg2
import traceback

DDL_DB_USER_NAME="ddlworker_db_user"
DDL_DB_NAME="ddlworker_db"
DDL_DB_HOST="localhost"

################################################################################

def connection():
    try:
        conn = psycopg2.connect(dbname=DDL_DB_NAME,
                                user=DDL_DB_USER_NAME,
                                password=DDL_DB_USER_NAME,
                                host=DDL_DB_HOST)

        return conn
    except psycopg2.Error as db_err:
        print("[DB::connection] [ERROR] {}".format(db_err))
        print(db_err.pgerror)
        return None

def disconnect(conn):
    conn.close()

def db_operation(operation):
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = connection()
            kwargs['conn'] = conn
            return operation(*args, **kwargs)
        except psycopg2.DatabaseError as db_err:
            print("[DB] [ERROR] DB Error: {}".format(db_err))
            return False, None

        except Exception as err:
            print("[DB] [ERROR] Unexpected Exception: {}".format(err))
            traceback.print_exc()
            return False, None
        finally:
            if conn is not None:
                disconnect(conn)
    return wrapper

################################################################################

@db_operation
def create_table(create_table_command, conn=None):
    assert(conn is not None)
    cur = conn.cursor()
    cur.execute(create_table_command)
    cur.close()
    conn.commit()
    return True, None

@db_operation
def table_exists(table_name, conn=None):
    assert(conn is not None)
    table_exists_command = "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='{}')".format(
                            table_name)

    cur = conn.cursor()
    cur.execute(table_exists_command)
    exists = cur.fetchone()[0]
    cur.close()
    return True, exists

@db_operation
def insert_table(insert_table_command, values, conn=None):
    assert(conn is not None)
    cur = conn.cursor()
    cur.execute(insert_table_command, values)
    conn.commit()
    cur.close()
    return True, None

@db_operation
def query_from_table(query_command, conn=None):
    assert(conn is not None)
    data = []
    cur = conn.cursor()
    cur.execute(query_command)
    row = cur.fetchone()
    while row is not None:
        row = cur.fetchone()
        data += [row]
    cur.close()
    return True, data