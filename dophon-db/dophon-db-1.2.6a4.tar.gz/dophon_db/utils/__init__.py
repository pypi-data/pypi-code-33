DICT = dict
OBJECT = object

# 定义返回类型(默认字典类型)
result_type = DICT


def get_db_cluster_info():
    from dophon_db import properties
    result = []
    for cluster in properties.db_cluster:
        alias = cluster.get('alias', 'default_db')
        host = cluster.get('host', 'localhost')
        port = cluster.get('port', 3306)
        db = cluster.get('database', 'database')
        user = cluster.get('user', 'root')
        password = cluster.get('password', 'root')
        chartset = cluster.get('chartset', 'utf8')
        tables = cluster.get('tables', []) if isinstance(cluster.get('tables'), list) else \
            [cluster.get('tables')] if 'tables' in cluster else []
        result.append({
            alias: {
                'alias': alias,
                '__host': host,
                '__port': port,
                '__database': db,
                '__user': user,
                '__password': password,
                '__chartset': chartset,
                'table_list': tables
            }
        })
    return result


def sort_result(data: list, description: tuple, result: list) -> list:
    """
    # 整理结果集并返回
    :param data: 数据集
    :param description:数据描述
    :param result: 结果列表(或许产生多个集合)
    :return:
    """
    for index in range(len(data)):
        item = data[index]
        r_item = {}
        if result_type is DICT:
            for i in range(len(item)):
                colName = description[i][0]
                val = item[i]
                value = 'none'
                if type(val) is not type(None):
                    value = str(val)
                # 组装data
                r_item[colName] = value
            # 组装结果集
            result.append(r_item)
        elif result_type is OBJECT:
            class_obj = type(str(id(data)), (), {})
            # 组装返回临时类
            for i in range(len(item)):
                colName = description[i][0]
                val = item[i]
                value = None
                if type(val) is not type(None):
                    value = str(val)
                class_obj = c_prop(class_obj, colName, value, use_setter=False)
            result.append(class_obj())
    return result
