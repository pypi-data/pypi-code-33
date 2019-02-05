class JTOS:

    mappings = {
        "gt": ">",
        "lt": "<",
        "gte": ">=",
        "lte": "<=",
        "e": "=",
        "ne": "!=",
        "l": "LIKE",
        "nl": "NOT LIKE",
        "a": "AND",
        "o": "OR",
        'i': 'IN',
        'ni': 'NOT IN'
    }

    def __init__(self):
        pass

    def set_object(self):
        pass

    def parse_object(self, obj):
        query_string = ""

        if "select" in obj:
            query_string += self.build_select(obj["select"])
            if "join" in obj:
                query_string += self.build_join(obj["join"])
        elif "delete" in obj:
            query_string += self.build_delete(obj["delete"])
        if "where" in obj:
            query_string += self.build_where(obj["where"])
        if "select" in obj and "groupBy" in obj["select"]:
            query_string += self.build_group(obj["select"]["groupBy"])
        if "select" in obj and "orderBy" in obj["select"]:
            query_string += self.build_order(obj["select"]["orderBy"])
        if 'limit' in obj:
            query_string += ' LIMIT {}'.format(obj['limit'])
        if 'offset' in obj:
            query_string += ' OFFSET {}'.format(obj['offset'])
        print(query_string)
        return query_string.replace("  ", " ") + ";"

    @staticmethod
    def build_where(where_object):
        clauses = []
        for v in where_object:
            join = None
            if len(clauses) > 0:
                join = "AND" if "join" not in v else v["join"]
            val = "'{}'".format(v["val"])
            if isinstance(v["val"], int) or ('type' in v and v['type'] == 'sql'):
                val = v['val']
            clauses.append(
                " {0} {1} {2} {3}".format(
                    JTOS.mappings[join] if join in JTOS.mappings else "",
                    v['field'],
                    JTOS.mappings[v["op"]],
                    val,
                )
            )
        return " WHERE" + "".join(clauses)

    @staticmethod
    def build_select(select_object):
        f = ",".join(select_object["fields"])
        t = ",".join(select_object["tables"])
        select = "SELECT {0} FROM {1}".format(f, t)
        return select

    @staticmethod
    def build_join(join_object):
        f = join_object['conditions']['from']
        t = join_object['conditions']['to']
        jt = join_object['type']
        join = " {0} JOIN {1} ON {1}.{2} = {3}.{4}".format(jt, f['table'], f['field'], t['table'], t['field'])
        return join

    @staticmethod
    def build_order(order_object):
        fields = []
        for k, v in order_object.items():
            fields.append("{0} {1}".format(k, v.upper()))
        return " ORDER BY " + ", ".join(fields)

    @staticmethod
    def build_group(group_object):
        fields = []
        for field in group_object:
            fields.append(field)
        return " GROUP BY " + ", ".join(fields)

    @staticmethod
    def build_insert(insert_object):
        fields = ",".join(list(insert_object["values"].keys()))
        values = list(insert_object["values"].values())
        val_string = ""
        for k, v in enumerate(values):
            if isinstance(v, int):
                val_string += v
            else:
                val_string += "'{}'".format(v)
            if k is not len(values) - 1:
                val_string += ','

        insert_string = "INSERT INTO {0}({1}) VALUES({2})".format(insert_object['table'], fields, val_string)
        return insert_string

    @staticmethod
    def build_delete(delete_object):
        print(delete_object)
        t = delete_object['table']
        delete_string = "DELETE FROM {}".format(t)
        return delete_string

    @staticmethod
    def build_update(update_object):
        pass

    @staticmethod
    def build_create(create_object):
        pass


# TODO auth against existing models to prevent malicious usage

if __name__ == '__main__':
    j = JTOS()
    so_obj = {
        "select": {
            "tables": ["users"],
            "fields": ["email", "id", "password"],
            "orderBy": {"email": "ASC", "id": "desc"},
        }
    }
    query_string = j.parse_object(so_obj)

# {
#     select: {
#         tables: [
#             "",
#             ""
#         ],
#         fields: [
#             "",
#             ""
#         ],
#         orderBy: {
#            "field": "ASC"
#         }
#     }
#     where: {
#         field: {
#             op: gt | lt | nl,
#             cmp: 0
#             join: 'AND'
#         }
#     }
# }
