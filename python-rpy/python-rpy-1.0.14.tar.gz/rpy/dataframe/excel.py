# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import datetime
from decimal import Decimal
from itertools import count, islice, product, repeat

from rpy.functions import six
from rpy.functions.decorators import to_tuple
from rpy.functions.dispatch import Dispatch
from rpy.functions.encoding import force_text

XLSX_MYMETYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

class Formula(object):

    def __init__(self, formula):
        self.formula = formula

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.formula)

def _column_name_generator(alphabeth = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    for i in count(1):
        yield from map(''.join, product(*repeat(alphabeth, i)))

@to_tuple
def get_excel_names(r):
    return islice(_column_name_generator(), r)

write = Dispatch()



@write.dispatch(Formula)
def handle(self, value, y, x):
    return self.worksheet.write_formula(y, x, value.formula)

@write.dispatch(bool)
def handle(self, value, y, x):
    self.update_max_size(x, 4)
    return self.worksheet.write_formula(y, x, (value and '=TRUE' or '=FALSE'))

@write.dispatch((tuple, list, set, frozenset))
def handle(self, value, y, x):
    return write(self, "-".join([force_text(v) for v in value]), y, x)

@write.dispatch(datetime.timedelta)
def handle(self, value, y, x):
    return self.worksheet.write_formula(y, x, '=TIME(0, 0, 0) + (%s / 86400) - TIME(0, 0, 0)' % value.total_seconds())

@write.dispatch(datetime.datetime)
def handle(self, value, y, x):
    self.update_max_size(x, 18)
    return self.worksheet.write_formula(y, x, '=DATE(%s, %s, %s) + (%s * 3600 + %s * 60 + %s) / 86400' % (
        value.year,
        value.month,
        value.day,
        value.hour,
        value.minute,
        value.second + value.microsecond / 1000000,
        ),
        cell_format = self.get_format('datetime_format', 'dd-mmm-yy hh:mm:ss')
    )

@write.dispatch(datetime.date)
def handle(self, value, y, x):
    self.update_max_size(x, 9)
    return self.worksheet.write_formula(y, x, '=DATE(%s, %s, %s)' % (value.year, value.month, value.day),
        cell_format = self.get_format('date_format', 15)
        )

@write.dispatch(datetime.time)
def handle(self, value, y, x):
    self.update_max_size(x, 8)
    return self.worksheet.write_formula(y, x, '=TIME(%s, %s, %s) + (%s / 86400)' % (
        value.hour,
        value.minute,
        value.second,
        value.microsecond / 1000000,
        ),
        cell_format = self.get_format('time_format', 21)
        )

@write.dispatch(int)
def handle(self, value, y, x):
    return self.worksheet.write_formula(y, x, '=%s' % value,
        cell_format = self.get_format('int_format', 3) # #,##0
        )

@write.dispatch((float, Decimal))
def handle(self, value, y, x):
    return self.worksheet.write_formula(y, x, '=%s' % value,
        cell_format = self.get_format('dec_format', 4) # #,##0.00
        )

@write.dispatch(type(None))
def handle(self, value, y, x):
    pass

@write.dispatch()
def handle(self, value, y, x):
    value = force_text(value)
    self.update_max_size(x, len(value))
    return self.worksheet.write(y, x, value)

class XLSXWriter(object):

    def __init__(self, f, name = 'Workbook', freeze_rows = 1, auto_sizing = True):

        from xlsxwriter import Workbook

        self.stream = f
        self.worksheet = None
        self.workbook = Workbook(self.stream)
        self.formats = {}
        self.worksheet = None
        if name:
            self.new_worksheet(name = name)
        self.freeze_rows = freeze_rows
        self.auto_sizing = auto_sizing

    def new_worksheet(self, name = None):

        self.close_worksheet()

        self.line = 0
        self.worksheet = self.workbook.add_worksheet(name = name)
        self.max = {}

    def get_format(self, name, value):
        try:
            return self.formats[name]
        except KeyError:
            if isinstance(value, six.integer_types):
                fmt = self.workbook.add_format()
                fmt.set_num_format(value)
            elif isinstance(value, six.string_types):
                fmt = self.workbook.add_format({'num_format': value})
            else:
                fmt = self.workbook.add_format(value)

            self.formats[name] = fmt
            return self.formats[name]

    def update_max_size(self, x, l):
        self.max[x] = max(l, self.max.get(x, 0))

    def close_worksheet(self):

        if self.worksheet:
            if self.freeze_rows:

                for i in range(self.freeze_rows):
                    self.worksheet.set_row(i, None, self.get_format(
                        'freezed_rows',
                        {'bold': True, 'bg_color': 'black', 'font_color': 'white'}
                    ))

            if self.auto_sizing:
                for y, l in self.max.items():
                    self.worksheet.set_column(y, y, l)

        self.worksheet = None

    write = write.as_method()

    def writerow(self, row):
        for y, value in enumerate(row):
            self.write(value, self.line, y)
        self.line += 1

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def close(self):
        self.close_worksheet()
        self.workbook.close()

def write_to_stream(lines, stream = None, **opts):
    s = stream or six.BytesIO()
    if not isinstance(lines, dict):
        lines = {'Data': lines}
    with XLSXWriter(s, name = None, **opts) as writer:
        for book, data in lines.items():
            writer.new_worksheet(book)
            for line in data:
                writer.writerow(line)
    if hasattr(s, 'seek'):
        s.seek(0)
    return s
