from sqlite3 import Cursor

type_dict = {'str': 'text', 'bool': 'int', 'float': 'real', 'int': 'int'}


def create_table_if_need(obj: object, conn):
    """
        根据任意对象obj成员对象来创建表
        obj的成员对象必须赋初始值
    """
    table_name = obj.__class__.__name__
    cursor = conn.cursor()

    sql = 'create table if not exists %s ( id  integer primary key autoincrement, ' % table_name
    for attr in dir(obj):
        if attr.startswith('__') and attr.endswith('__'):
            continue
        if attr == 'id':
            continue
        cls_type = obj.__getattribute__(attr).__class__.__name__
        sql_type = type_dict.get(cls_type)
        sql += attr + " " + sql_type + ","

    sql = sql.strip().rstrip(',') + ");"
    cursor.execute(sql)
    conn.commit()
    cursor.close()


def insert(obj: object, conn):
    table_name = obj.__class__.__name__

    cursor = conn.cursor()
    attrs = [attr for attr in dir(obj) if not attr.startswith('__') and not attr.endswith('__')]
    attrs_name = ','.join(attrs)

    values = ''
    for attr in attrs:
        attr_value = obj.__getattribute__(attr)
        if attr_value.__class__ == str:
            values += "'%s'," % attr_value
        elif attr_value.__class__ == bool:
            if attr_value:
                values += str(1)
            else:
                values += str(0)
            values += ","
        else:
            values += str(attr_value) + ","
    attrs_value = values[0: len(values) - 1]
    sql = 'insert into %s (%s) values (%s)' % (table_name, attrs_name, attrs_value)

    try:
        cursor.execute(sql)
    except Exception as e:
        raise e

    conn.commit()
    cursor.close()
    return True


def query(obj: object, conn):
    """
    搜索
    :param conn:
    :param obj: 搜索对象
    :return: 搜索结果
    """
    table_name = obj.__class__.__name__

    cursor = conn.cursor()

    cursor.execute("select * from %s where id = %d" % (table_name, obj.id))

    result = cursor.fetchone()
    cursor.close()
    conn.commit()
    return result


def query_all(obj: object, conn):
    """
        搜索
        :param conn:
        :param obj: 搜索对象
        :return: 搜索结果
        """
    table_name = obj.__class__.__name__

    cursor = conn.cursor()

    cursor.execute("select * from %s" % table_name)
    assert isinstance(cursor, Cursor)
    data = cursor.fetchall()
    result = []
    for item in data:
        new_obj = obj.__class__()
        attrs = [attr for attr in dir(obj) if not attr.startswith('__') and not attr.endswith('__')]
        for i in range(len(attrs)):
            attr = attrs[i]
            new_obj.__setattr__(attr, item[i + 1])
        result.append(new_obj)
    cursor.close()
    conn.commit()
    return result
