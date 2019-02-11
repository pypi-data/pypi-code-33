from django.db import connections
from functools import reduce


class QueryTool():

    db = ''
    table = ''

    def __init__(self, db, table):
        self.db = db
        self.table = table
        self.query = ''

    def get(self, condition):
        return self.select().where(condition).first()

    def run(self):
        with connections[self.db].cursor() as cursor:
            cursor.execute(self.query)
            return dictfetchall(cursor)

    def first(self):
        return self.run()[0] 

    def select(self, *args):
        if args == ():
            args = '*',
        field_strings = ', '.join(args)
        self.query = self.__select_from(field_strings)
        return self

    def where(self, condition):
        self.query = self.query + ' WHERE ' + ' ' + condition
        return self

    def order_by(self, field, order='desc'):
        if order != 'desc' and order != 'asc':
            raise NameError('Query ORDER BY order must be either desc or asc')
        self.query = self.query + ' ORDER BY ' + field + ' ' + order
        return self

    def limit(self, limit):
        if type(limit) is not int:
            raise TypeError('Query LIMIT must be int')
        self.query = self.query + ' LIMIT ' + str(limit)
        return self

    def __select_from(self, fields_string):
        return 'SELECT {} FROM {} '.format(fields_string, self.table)


def comma_separated_string(*strings):
        return reduce((lambda x, y: x + ', ' + y), list(strings))


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
