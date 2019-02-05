# -*- coding: utf-8 -*-
"""
    This module will create a seaborn table which acts a dictionary
        and a list. It makes handling some raw data very quick and
        convenient.

    It can do this by consuming:
        list of list
        list of dictionary
        dictionary of dictionary
        dictionary of lists

    It can consume these from raw python data structures, csv, text,
    or mark down files. It can output to csv, text, markdown or html.

    This is primarily as a library but can be used as a script with:
    > seaborn_table source_file destination_file
"""
import os
import sys
from collections import OrderedDict
from functools import reduce


class SeabornTable(object):
    DEFAULT_DELIMINATOR = u'\t'
    DEFAULT_TAB = u''
    ENCODING = 'utf-8'
    FANCY = {
        'top edge': u'═',
        'top intersect': u'╤',
        'top left corner': u'╒',
        'top right corner': u'╕',

        'internal horizontal edge': u'─',
        'internal intersect': u'┼',
        'internal major intersect': u'╪',
        'internal vertical edge': u'│',

        'left major intersect': u'╞',
        'left intersect': u'├',
        'left edge': u'│',

        'right major intersect': u'╡',
        'right intersect': u'┤',
        'right edge': u'│',

        'bottom edge': u'═',
        'bottom intersect': u'╧',
        'bottom left intersect': u'╘',
        'bottom right corner': u'╛',
    }

    def __init__(self, table=None, columns=None, row_columns=None, tab=None,
                 key_on=None, deliminator=None):
        """
        :param table: obj can be list of list or list of dict
        :param columns: list of str of the columns in the table
        :param row_columns: list of str if different then visible columns
        :param tab: str to include before every row
        :param key_on: tuple of str if assigned so table is accessed as dict
        :param deliminator: str to separate the columns such as , \t or |
        """
        self._deliminator = self.DEFAULT_DELIMINATOR
        self._tab = self.DEFAULT_TAB
        self._row_columns = []
        self._column_index = OrderedDict()
        if columns:
            columns = list(columns)
        if row_columns:
            row_columns = list(row_columns)

        # normalize table to a list of SeabornRows
        if not table:
            self.row_columns = columns or row_columns or []
            self.table = []
        elif isinstance(table, SeabornTable):
            columns = columns or table.columns.copy()
            self.row_columns = table.row_columns
            self.table = [SeabornRow(self._column_index, list(row) + [])
                          for row in table]
        elif isinstance(table, list) and isinstance(table[0], SeabornRow):
            self._column_index = table[0].column_index
            self._row_columns = list(table[0].column_index.keys())
            self.table = table
        elif isinstance(table, dict):
            temp = self.dict_to_obj(table, columns, row_columns,
                                            key_on=key_on)
            self._column_index, self.table = temp._column_index, temp.table
            self._row_columns = list(self._column_index.keys())
        elif isinstance(table, list):
            temp = self.list_to_obj(table, columns, row_columns,
                                            key_on=key_on)
            self._column_index, self.table = temp._column_index, temp.table
            self._row_columns = list(self._column_index.keys())
        elif getattr(table, 'headings', None) is not None and \
                getattr(table, 'row_columns', None) is not None:
            self.row_columns = row_columns or columns or table.headings
            self.table = [SeabornRow(self._column_index,
                                     [row[c] for c in self.row_columns])
                          for row in table]
        else:
            raise TypeError("Unknown type of table")

        self._parameters = {}
        self.tab = self.DEFAULT_TAB if tab is None else tab
        self.deliminator = self.DEFAULT_DELIMINATOR if deliminator is None \
            else deliminator
        self._key_on = None
        self.key_on = key_on
        self._columns = columns or self.row_columns

        for column in self._columns:
            if column not in self._column_index:
                # noinspection PyTypeChecker
                self.insert(None, column, None)
        self.assert_valid()

    @classmethod
    def list_to_obj(cls, list_, columns, row_columns=None, tab='',
                    key_on=None):
        """
        :param list_: list of list or list of dictionary to use as the source
        :param columns: list of strings to label the columns on print out
        :param row_columns: list of columns in the actually data
        :param tab: str of the tab to use before the row on printout
        :param key_on: str of the column to key each row on
        :return: SeabornTable
        """
        if getattr(list_[0], 'keys', None) and not isinstance(list_[0], dict):
            row_columns = row_columns or columns or list_[0].keys()
            column_index = cls._create_column_index(row_columns)
            table = [SeabornRow(
                column_index,
                [getattr(row, col, None) for col in row_columns])
                for row in list_]
        elif isinstance(list_[0], dict):
            row_columns = row_columns or columns or \
                          cls._key_on_columns(key_on,
                                              cls._get_normalized_columns(
                                                  list_))
            column_index = cls._create_column_index(row_columns)
            table = [SeabornRow(column_index,
                                [row.get(c, None) for c in row_columns])
                     for row in list_]

        elif isinstance(list_[0], (list, tuple)) and len(list_) == 1:
            row_columns = row_columns or columns or \
                          cls._key_on_columns(key_on, [
                              'Column %s' % i for i in range(len(list_[0]))])
            column_index = cls._create_column_index(row_columns)
            table = [SeabornRow(column_index, row) for row in list_]

        elif isinstance(list_[0], (list, tuple)):
            row_columns = row_columns or columns or []
            if len(row_columns) < len(list_[0]):
                row_columns = list_[0]
            if list_[0] == row_columns:
                list_ = list_[1:]
            column_index = cls._create_column_index(row_columns)
            size = len(row_columns)
            table = [SeabornRow(column_index, row + [None] * (size - len(row)))
                     for row in list_]
        else:
            column_index = cls._create_column_index(columns or [])
            table = [SeabornRow(column_index, [row]) for row in list_]

        return cls(table, columns, row_columns, tab, key_on)

    @classmethod
    def dict_to_obj(cls, dict_, columns, row_columns, tab='', key_on=None):
        """
        :param dict_: dict of dict or dict of list
        :param columns: list of strings to label the columns on print out
        :param row_columns: list of columns in the actually data
        :param tab: str of the tab to use before the row on printout
        :param key_on: str of the column to key each row on
        :return: SeabornTable
        """
        if isinstance(list(dict_.values())[0], dict):
            row_columns = row_columns or columns or cls._key_on_columns(
                key_on, cls._ordered_keys(dict_.values()[0]))
            column_index = cls._create_column_index(row_columns)
            if key_on is None:
                table = [
                    SeabornRow(column_index, [row[c] for c in row_columns])
                    for row in dict_.values()]
            else:
                table = [SeabornRow(column_index,
                                    [row.get(c, c == key_on and key or None)
                                     for c in row_columns])
                         for key, row in dict_.items()]

        elif isinstance(list(dict_.values())[0], list):
            row_columns = row_columns or columns or \
                          cls._key_on_columns(key_on, sorted(dict_.keys()))
            column_index = cls._create_column_index(row_columns)
            if key_on is None:
                table = [
                    SeabornRow(column_index, [dict_[c][i] for c in columns])
                    for i in range(len(dict_[columns[0]]))]
            else:
                table = [
                    SeabornRow(column_index, [dict_[c][i] for c in columns])
                    for i in range(len(dict_[columns[0]]))]

        else:
            row_columns = row_columns or columns or ['KEY', 'VALUE']
            column_index = cls._create_column_index(row_columns)
            table = [SeabornRow(column_index, [k, v]) for k, v in
                     dict_.items()]

        return cls(table, columns, row_columns, tab, key_on)

    @classmethod
    def csv_to_obj(cls, file_path=None, text='', columns=None,
                   remove_empty_rows=True, key_on=None):
        """
        This will convert a csv file or csv text into a seaborn table
        and return it
        :param file_path: str of the path to the file
        :param text: str of the csv text
        :param columns: list of str of columns to use
        :param remove_empty_rows: bool if True will remove empty rows
                which can happen in non-trimmed file
        :param key_on: list of str of columns to key on
        :return: SeabornTable
        """
        data = []
        lines = cls._get_lines(file_path, text, replace=u'\ufeff')
        for i in range(len(lines)):
            lines[i] = lines[i].replace('\r', '\n')
            lines[i] = lines[i].replace('\\r', '\r').split(',')
        line_index = 0
        while line_index < len(lines):
            cells = lines[line_index]
            line_index += 1
            i = 0
            row = []
            while i < len(cells):
                cell = cells[i]  # this is slow in pycharm debug
                i += 1
                while cell.count('"') % 2:
                    if i >= len(cells):  # excel causes this to happen
                        cells += lines[line_index]
                        cell += "\n" + cells[i]  # add the line break back in
                        line_index += 1
                    else:
                        cell += ',' + cells[i]
                    i += 1
                cell = cls._eval_cell(cell, True)

                row.append(cell)
            if not remove_empty_rows or True in [bool(r) for r in row]:
                data.append(row)

        row_columns = data[0]
        if len(row_columns) != len(set(row_columns)):  # make unique
            for i, col in enumerate(row_columns):
                count = row_columns[:i].count(col)
                row_columns[i] = '%s_%s' % (col, count) if count else col

        return cls.list_to_obj(data[1:], columns=columns,
                               row_columns=row_columns, key_on=key_on)

    @classmethod
    def grid_to_obj(cls, file_path=None, text='', delim=None,
                    columns=None, key_on=None):
        """
        This will convert a grid file or grid text into a seaborn table
        and return it
        :param file_path: str of the path to the file
        :param text: str of the grid text
        :param columns: list of str of columns to use
        :param key_on: list of str of columns to key on
        :return: SeabornTable
        """
        delim = delim if delim else cls.FANCY
        lines = cls._get_lines(file_path, text)
        data=[]
        for i in range(len(lines)):
            if i % 2 == 1:
                row = lines[i].split(delim['internal vertical edge'])[1:-1]
                data.append([cls._eval_cell(r) for r in row])
        row_columns = data[0]
        if len(row_columns) != len(set(row_columns)): # make unique
            for i, col in enumerate(row_columns):
                count = row_columns[:i].count(col)
                row_columns[i] = '%s_%s'%(col, count) if count else col
        return cls.list_to_obj(data[1:], columns=columns,
                               row_columns=row_columns, key_on=key_on)

    @classmethod
    def file_to_obj(cls, file_path, columns=None):
        if file_path.endswith('.txt'):
            return cls.str_to_obj(file_path=file_path, columns=columns)
        elif file_path.endswith('.grid'):
            return cls.grid_to_obj(file_path=file_path, columns=columns)
        elif file_path.endswith('.md'):
            return cls.mark_down_to_obj(file_path=file_path, columns=columns)
        elif file_path.endswith('.csv'):
            return cls.csv_to_obj(file_path=file_path, columns=columns)
        elif file_path.endswith('.grid'):
            return cls.grid_to_obj(file_path=file_path, columns=columns)
        else:
            raise 'Unknown file type: %s' % file_path

    @classmethod
    def str_to_obj(cls, file_path='', text='', columns=None,
                   remove_empty_rows=True, key_on=None,
                   row_columns=None, deliminator='\t', eval_cells=True):
        """
        This will convert a csv file or csv text into a seaborn table
        and return it
        :param file_path: str of the path to the file
        :param text: str of the csv text
        :param columns: list of str of columns to use
        :param row_columns: list of str of columns in data but not to use
        :param remove_empty_rows: bool if True will remove empty rows
        :param key_on: list of str of columns to key on
        :param deliminator: str to use as a deliminator
        :param eval_cells: bool if True will try to evaluate numbers
        :return: SeabornTable
        """
        text = cls._get_lines(file_path, text)
        if len(text) == 1:
            text = text[0].split('\r')

        eval_cell = cls._eval_cell if eval_cells else lambda x: x
        list_of_list = [[eval_cell(cell) for cell in row.split(deliminator)]
                        for row in text if not remove_empty_rows or
                        True in [bool(r) for r in row]]

        if list_of_list[0][0] == '' and list_of_list[0][-1] == '':
            list_of_list = [row[1:-1] for row in list_of_list]

        return cls.list_to_obj(list_of_list, key_on=key_on, columns=columns,
                               row_columns=row_columns)

    @classmethod
    def mark_down_to_dict_of_obj(cls, file_path=None, text='', columns=None,
                                 key_on=None):
        """
        This will read multiple tables separated by a #### Header
        and return it as a dictionary of headers
        :param file_path: str of the path to the file
        :param text: str of the mark down text
        :param columns: list of str of columns to use
        :param key_on: list of str of columns to key on
        :return: OrderedDict of {<header>: SeabornTable}
        """
        text = cls._get_lines(file_path, text, split_lines=False)
        ret = OrderedDict()
        paragraphs = text.split('####')
        for paragraph in paragraphs[1:]:
            header, text = paragraph.split('\n', 1)
            ret[header.strip()] = cls.mark_down_to_obj(text=text,
                                                       columns=columns,
                                                       key_on=key_on)
        return ret

    @classmethod
    def mark_down_to_obj(cls, file_path=None, text='', columns=None,
                         key_on=None, ignore_code_blocks=True):
        """
        This will convert a csv file or csv text into a seaborn table
         and return it
        :param file_path: str of the path to the file
        :param text: str of the mark down text
        :param columns: list of str of columns to use
        :param key_on: list of str of columns to key on
        :param ignore_code_blocks: bool if true will filter out
            any lines between ```
        :return: SeabornTable
        """
        text = cls._get_lines(file_path, text, split_lines=False)

        if ignore_code_blocks:
            text = text.split("```")
            for i in range(1, len(text), 2):
                text.pop(i)
            text = (''.join(text)).strip()

        assert text.startswith('|') and text.endswith(
            '|'), "Unknown format for markdown table"

        table = []
        for row in text.split('\n'):
            row = row.strip()
            if row == '':
                continue
            assert row[0] == '|' and row[-1] == '|', \
                'The following line is formatted correctly: %s' % row
            table.append([cls._clean_cell(cell) for cell in
                          row[1:-1].split('|')])
        return cls(table=table[2:], columns=columns or table[0], key_on=key_on)

    @classmethod
    def objs_to_mark_down(cls, tables, file_path=None, keys=None,
                          pretty_columns=True):
        """
        :param tables:         dict of {str <name>:SeabornTable}
        :param file_path:      str of the path to the file
        :param keys:           list of str of the order of keys to use
        :param pretty_columns: bool if True will make the columns pretty
        :return:               str of the converted markdown tables
        """
        keys = keys or tables.keys()
        ret = ['#### ' + key + '\n' + tables[key].obj_to_mark_down(
            pretty_columns=pretty_columns) for key in keys]
        ret = '\n\n'.join(ret)
        cls._save_file(file_path, ret)
        return ret

    def obj_to_mark_down(self, file_path=None, title_columns=True,
                         quote_numbers=True):
        """
        This will return a str of a mark down text
        :param title_columns: bool if True will title all headers
        :param file_path: str of the path to the file to write to
        :param quote_numbers: bool if True will quote number
        :return: str
        """
        md = [[self._title_column(col) if title_columns else str(col) for col
               in self.columns]]
        md += [[self._safe_str(row[col], quote_numbers)
                for col in self.columns] for row in self.table]

        column_widths = self._get_column_widths(md, pad_last_column=True)
        md.insert(1, [u":" + u'-' * (width - 1) for width in column_widths])
        md = [u'| '.join([row[c].ljust(column_widths[c])
                          for c in range(len(row))]) for row in md]
        ret = u'| ' + u' |\n| '.join(md) + u' |'
        self._save_file(file_path, ret)
        return ret

    def obj_to_str(self, file_path=None, deliminator=None, tab=None):
        deliminator = self.deliminator if deliminator is None \
            else deliminator
        tab = self.tab if tab is None else tab

        list_of_list = [[self._safe_str(cell, quote_numbers=False)
                         for cell in row] for row in self]
        list_of_list = [self.columns] + list_of_list

        column_widths = self._get_column_widths(list_of_list, padding=0)
        ret = [[cell.ljust(column_widths[i]) for i, cell in enumerate(row)]
               for row in list_of_list]

        ret = [deliminator.join(row) for row in ret]
        ret = tab + (u'\n' + tab).join(ret)
        self._save_file(file_path, ret)
        return ret

    def obj_to_grid(self, file_path=None, delim=None, tab=None):
        """
        :param file_path: path to data file, defaults to
                            self's contents if left alone
        :param delim:     dict of deliminators, defaults to
                            obj_to_str's method:
        :param tab:     string of offset of the table
        :return:        string representing the grid formation
                        of the relevant data
        """

        div_delims = {"top": ['top left corner', 'top intersect',
                              'top edge', 'top right corner'],
                      "divide": ['left major intersect',
                                 'internal major intersect',
                                 'bottom edge', 'right major intersect'],
                      "middle": ['left intersect', 'internal intersect',
                                 'internal horizontal edge', 'right intersect'],
                      "bottom": ['bottom left intersect', 'bottom intersect',
                                 'bottom edge', 'bottom right corner']}
        delim = delim if delim else {}
        for tag in self.FANCY.keys():
            delim[tag] = delim[tag] if tag in delim.keys() \
                else self.FANCY[tag]

        tab = self.tab if tab is None else tab

        list_of_list = [[self._safe_str(cell, quote_numbers=False)
                         for cell in row] for row in self]
        list_of_list = [self.columns] + list_of_list

        column_widths = self._get_column_widths(list_of_list,
                                                padding=0, pad_last_column=True)
        ret = [[cell.ljust(column_widths[i]) for i, cell in enumerate(row)]
               for row in list_of_list]
        grid_row={}

        for key in div_delims.keys():
            draw = div_delims[key]
            grid_row[key] = delim[draw[0]]
            grid_row[key] += delim[draw[1]].join(
                [delim[draw[2]] * width
                 for width in column_widths])
            grid_row[key] += delim[draw[3]]

        ret = [delim['left edge']+delim['internal vertical edge'].join(row)+
               delim['right edge'] for row in ret]
        header = [grid_row["top"], ret[0], grid_row["divide"]]
        body = [[row, grid_row["middle"]] for row in ret[1:]]
        body = [item for pair in body for item in pair][:-1]
        ret = header + body + [grid_row["bottom"]]
        ret = tab + (u'\n'+tab).join(ret)
        self._save_file(file_path, ret)
        return ret


    def obj_to_csv(self, quote_everything=False, space_columns=True,
                   file_path=None):
        """
        This will return a str of a csv text that is friendly to excel
        :param quote_everything: bool if True will quote everything if it needs
            it or not
        :param space_columns: bool if True it will align columns with spaces
        :param file_path: str to the path
        :return: str
        """
        csv = [[self._excel_cell(cell, quote_everything)
                for cell in self.columns]]
        csv += [[self._excel_cell(row[col], quote_everything)
                 for col in self.columns] for row in self.table]

        if space_columns:
            column_widths = self._get_column_widths(csv, padding=0)
            csv = [','.join([cell.ljust(column_widths[i])
                             for i, cell in enumerate(row)]) for row in csv]
        else:
            csv = [','.join(row) for row in csv]

        if os.name == 'posix':
            ret = '\r\n'.join(csv)
        else:
            ret = '\n'.join(csv)

        self._save_file(file_path, ret)
        return ret

    def obj_to_html(self, tab='', border=1, cell_padding=5, cell_spacing=1,
                    border_color='black', align='center', row_span=None,
                    file_path=None):
        """
        This will return a str of an html table.
        :param tab: str to insert before each line e.g. '    '
        :param border: int of the thickness of the table lines
        :param cell_padding: int of the padding for the cells
        :param cell_spacing: int of the spacing for hte cells
        :param border_color: str of the color for the border
        :param align: str for cell alignment, center, left, right
        :param row_span: list of rows to span
        :param file_path: str for path to the file
        :return: str of html code
        """
        html_table = self._html_link_cells()
        html_table._html_row_respan(row_span)
        data = [self._html_row(html_table.columns, tab + '  ', '#bcbcbc',
                               align=align)]
        for i, row in enumerate(html_table):
            color = '#dfe7f2' if i % 2 else None
            row = [row[c] for c in html_table.columns]
            data.append(self._html_row(row, tab + '  ', color, align=align))

        ret = '''
            <table border="%s" cellpadding="%s" cellspacing="%s"
                   bordercolor="%s" >
              %s
            </table>'''.strip().replace('\n            ', '\n')

        data = ('\n%s  ' % tab).join(data)
        ret = (ret % (border, cell_padding, cell_spacing, border_color, data)
               ).replace('\n', '\n%s' % tab)
        self._save_file(file_path, ret)
        return ret

    def obj_to_file(self, file_path):
        if file_path.endswith('.txt'):
            self.obj_to_str(file_path=file_path)
        elif file_path.endswith('.csv'):
            self.obj_to_csv(file_path=file_path)
        elif file_path.endswith('html'):
            self.obj_to_html(file_path=file_path)
        elif file_path.endswith('md'):
            self.obj_to_mark_down(file_path=file_path, title_columns=False)
        elif file_path.endswith('grid'):
            self.obj_to_grid(file_path=file_path)
        else:
            raise Exception('Unknown file type: %s' % file_path)

    @property
    def tab(self):
        return self._tab

    @tab.setter
    def tab(self, value):
        if sys.version_info[0] == 2:
            value = value.decode(self.ENCODING)
        self._tab = value

    @property
    def deliminator(self):
        return self._deliminator

    @deliminator.setter
    def deliminator(self, value):
        if sys.version_info[0] == 2:
            value = value.decode(self.ENCODING)
        self._deliminator = value

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, column_names):
        assert isinstance(column_names, (list, tuple))
        for col in column_names:
            if col not in self._column_index:
                self.row_columns += [col]
                for row in self:
                    row.append(None)
        self._columns = column_names

    @property
    def row_columns(self):
        return self._row_columns

    @row_columns.setter
    def row_columns(self, value):
        assert len(set(value)) == len(value), "Columns must be unique"
        self._row_columns = list(value)
        self._column_index.clear()
        for index, col in enumerate(value):
            self._column_index[col] = index

    @property
    def key_on(self):
        return self._key_on

    @key_on.setter
    def key_on(self, value):
        """
        :param value: str of which column to key the rows on like a dictionary
        :return: None
        """
        if isinstance(value, BASESTRING):
            value = (value,)
        self._key_on = value

    @property
    def parameters(self):
        return self._parameters

    def map(self, func):
        """
        This will replace every cell in the function with func(cell)
        :param func: func to call
        :return: None
        """
        for row in self.table:
            for i, cell in enumerate(row):
                row[i] = func(cell)

    def assert_valid(self):
        for c in self._columns:
            if c not in self.row_columns:
                raise Exception(
                    'Column "%s" is in columns but not in row_columns' % c)
            if not isinstance(c, BASESTRING):
                raise Exception(
                    'Column "%s" is "%s" and not a string' % (c, type(c)))

        for row in self:
            if row.column_index != self._column_index:
                raise Exception("Table row_columns does not match row columns:"
                                " \n%s\n%s" % (self._column_index, row))
            if len(row) > len(self.row_columns):
                raise Exception("Row has more values then the SeabornTable "
                                "columns: \n%s\n%s" % (self.row_columns, row))
            if len(row) < len(self.row_columns):
                raise Exception("Row has less values then the SeabornTable "
                                "columns: \n%s\n%s" % (self.row_columns, row))

    def naming_convention_columns(self, convention='underscore',
                                  remove_empty=True):
        """
        This will change the column names to a particular naming convention.
            underscore: lower case all letters and replaces spaces with _
            title: uppercase first letter and replaces _ with spaces
        :param convention: str enum of "lowercase_underscore"
        :param remove_empty: bool if true will remove column header of value ''
        :return: None
        """
        converter = getattr(self, '_%s_column' % convention, None)
        assert converter is not None, \
            'Convention "%s" is not a valid convention' % convention
        self.row_columns = [converter(col) for col in self.row_columns]
        self._columns = [converter(col) for col in self._columns]
        if remove_empty and '' in self.row_columns:
            self.remove_column('')

    def remove_column(self, key):
        """
        :param key: str of the column to remove from every row in the table
        :return: None
        """
        if not isinstance(key, int):
            key = self._column_index[key]
        for row in self.table:
            row.pop(key)
        self.row_columns = [i for i, c in enumerate(self.row_columns) if
                            i + key]

    def filter_by(self, **kwargs):
        """
        :param kwargs: dict of column == value
        :return: SeabornTable
        """
        ret = self.__class__(
            columns=self.columns, row_columns=self.row_columns, tab=self.tab,
            key_on=self.key_on)
        for row in self:
            if False not in [row[k] == v for k, v in kwargs.items()]:
                ret.append(row)
        return ret

    def filter(self, column, condition='!=', value=None):
        """
        :param column: str or index of the column
        :param condition: str of the python operator
        :param value: obj of the value to test for
        :return: SeabornTable
        """
        ret = self.__class__(
            columns=self.columns, row_columns=self.row_columns, tab=self.tab,
            key_on=self.key_on)
        for row in self:
            if getattr(row[column], condition, None):
                if eval('row[column].%s(%s)' % (condition, value)):
                    ret.append(row)
            if eval('row[column] %s value' % condition):
                ret.append(row)
        return ret

    def append(self, row=None):
        """
            This will add a row to the table
        :param row: obj, list, or dictionary
        :return: SeabornRow that was added to the table
        """
        self.table.append(self._normalize_row(row))
        return self.table[-1]

    def remove(self, row):
        assert row in self.table, 'Row %s was not in this table' % row
        self.table.remove(row)

    @classmethod
    def pertibate_to_obj(cls, columns, pertibate_values,
                         generated_columns=None, filter_func=None,
                         max_size=None, deliminator=None, tab=None):
        """
            This will create and add rows to the table by pertibating the
            parameters for the provided columns
        :param columns: list of str of columns in the table
        :param pertibate_values: dict of {'column': [values]}
        :param generated_columns: dict of {'column': func}
        :param filter_func: func to return False to filter out row
        :param max_size: int of the max size of the table
        :param deliminator: str to use as a deliminator when making a str
        :param tab: str to include before every row
        :return: SeabornTable
        """
        table = cls(columns=columns, deliminator=deliminator, tab=tab)
        table._parameters = pertibate_values.copy()
        table._parameters.update(generated_columns or {})
        table.pertibate(pertibate_values.keys(), filter_func, max_size)
        return table

    def pertibate(self, pertibate_columns=None, filter_func=None,
                  max_size=1000):
        """
        :param pertibate_columns: list of str fo columns to pertibate see DOE
        :param filter_func: func that takes a SeabornRow and return
                            True if this row should be exist
        :param max_size: int of the max number of rows to try
                            but some may be filtered out
        :return:  None
        """
        pertibate_columns = pertibate_columns or self.columns
        for c in pertibate_columns:
            assert c in self.columns, 'Column %s was not part of this self' % c

        # noinspection PyTypeChecker
        column_size = [c in pertibate_columns and len(self._parameters[c]) or 1
                       for c in self.columns]

        max_size = min(max_size, reduce(lambda x, y: x * y, column_size))

        for indexes in self._index_iterator(column_size, max_size):
            row = SeabornRow(self._column_index,
                             [self._pertibate_value(indexes.pop(0), c) for
                              c in self.columns])

            kwargs = row.obj_to_dict()
            if filter_func is None or filter_func(_row_index=len(self.table),
                                                  **kwargs):
                self.table.append(row)

        for c in self.columns:  # if the parameter is a dynamic function
            if hasattr(self._parameters.get(c, ''), '__call__'):
                # noinspection PyTypeChecker
                self.set_column(c, self._parameters[c])


    @classmethod
    def _get_lines(cls, file_path=None, text='', replace=None, split_lines=True):
        if file_path is not None:
            assert os.path.exists(file_path), \
                "Missing file: %s"%file_path
            with open(file_path, 'rb') as f:
                text = f.read()
        if (sys.version_info[0] == 3 and isinstance(text, bytes) or
            sys.version_info[0] == 2):
            text = text.decode(cls.ENCODING)

        if replace:
            text = text.replace(replace, u'')
        if split_lines:
            if text.find(u'\r\n') == -1:
                text = text.split(u'\n')
            else:
                text = text.split(u'\r\n')
        assert text, 'Text is empty'
        return text

    def __str__(self):
        ret = self.obj_to_str()
        if sys.version_info[0] == 2:
            ret = ret.encode(self.ENCODING)
        return ret

    def __unicode__(self):
        return self.obj_to_str()

    def __repr__(self):
        return '%s<rows=%s, cols=%s>' % (
            self.__class__.__name__, len(self), len(self.columns))

    def __add__(self, other):
        column_index = self._create_column_index(
            self.row_columns +
            [c for c in other.row_columns if c not in self._column_index])
        new_table = []
        for row in self.table + other.table:
            new_table.append(
                SeabornRow(column_index,
                           [row.get(c, None) for c in column_index]))

        return self.__class__(table=new_table, columns=self.columns)

    def __eq__(self, other):
        if not isinstance(other, SeabornTable):
            other = self.__class__(other)
        return self.table.__eq__(other.table)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if not isinstance(other, SeabornTable):
            other = self.__class__(other)
        return self.table.__gt__(other.table)

    def __lt__(self, other):
        if not isinstance(other, SeabornTable):
            other = self.__class__(other)
        return self.table.__lt__(other.table)

    def __ge__(self, other):
        if not isinstance(other, SeabornTable):
            other = self.__class__(other)
        return self.table.__ge__(other.table)

    def __le__(self, other):
        if not isinstance(other, SeabornTable):
            other = self.__class__(other)
        return self.table.__le__(other.table)

    def __len__(self):
        return len(self.table)

    def __contains__(self, value):
        if not isinstance(value, (tuple, list, dict, SeabornRow)) and \
                self.key_on and len(self.key_on) == 1:
            value = [value]

        if isinstance(value, (tuple, list)) and self.key_on and len(
                value) == len(self.key_on):
            for row in self.table:
                key = [row[k] for k in self.key_on]
                if key == list(value):
                    return True
            return False
        elif (isinstance(value, SeabornRow) and
              getattr(value, 'column_index') == self._column_index):
            return value in self.table
        elif isinstance(value, SeabornRow):
            value = [value[k] for k in self.row_columns]
            for row in self.table:
                if [row[k] for k in self.row_columns] == value:
                    return True
            return False

        elif isinstance(value, (tuple, list, dict)):
            return self._normalize_row(value) in self.table

    def __getitem__(self, item):
        """
            This will return a row if item is an int or if key_on is set
            else it will return the column if column if it is in self._columns
        :param item: int or str of the row or column to get
        :return: list
        """
        if isinstance(item, (int, slice)):
            return self.table[item]
        else:
            assert self.key_on
            if not isinstance(item, (tuple, list)):
                item = [item]

            for row in self.table:
                key = [row[k] for k in self.key_on]
                if key == list(item):
                    return row

            row = self.append()
            for i, key in enumerate(self.key_on):
                row[key] = item[i]
            return row

    def __setitem__(self, item, value):
        """
            This will set a row if item is an int or set the values of a column
        :param item: int or str of the row or column to set
        :param value: func or obj or list if it is a list then assign each row
            from this list
        :return: None
        """
        if isinstance(item, int):
            self.table[item] = self._normalize_row(value)
        else:
            assert self.key_on
            if not isinstance(item, (tuple, list)):
                item = [item]

            for i, row in enumerate(self.table):
                key = [row[k] for k in self.key_on]
                if key == list(item):
                    self.table[i] = value
                    return

            row = self.append(value)
            for i, key in enumerate(self.key_on):
                row[key] = item[i]

    def pop_column(self, column):
        self.columns = [c for c in self.columns if c != column]

    def keys(self):
        return self.columns

    def has_key(self, item):
        return item in self.columns

    def clear(self):
        self.table = []

    def copy(self, share_rows=False):
        if share_rows:
            return self.__class__(self.table, self.columns, self.row_columns,
                                  self.tab, self.key_on, self.deliminator)
        else:
            return self.__class__(self, self.columns, self.row_columns,
                                  self.tab, self.key_on, self.deliminator)

    def set_column(self, item, value=None):
        if hasattr(value, '__call__'):
            value = [value(_row_index=r, **self.table[r].obj_to_dict()) for r
                     in range(len(self.table))]
        else:
            value = isinstance(value, list) and value or [value] * len(self)

        if item not in self._column_index:
            self.row_columns += [item]
            for row in self.table:
                row.append(None)

        index = self._column_index[item]
        for i, row in enumerate(self.table):
            row[index] = value[i]

    def insert(self, index, column, default_value='', values=None,
               compute_value_func=None, compute_key=None):
        """
            This will insert a new column at index and then set the value
            unless compute_value is provided
        :param index: int index of where to insert the column
        :param column: str of the name of the column
        :param default_value: obj of the default value
        :param values: obj of the column values (length should equal table)
        :param compute_value_func: func to compute the value given the row
        :param compute_key: str of the column to send to computer_value_func
                instead of row
        :return: None
        """
        for row in self.table:
            value = values.pop(0) if values else default_value
            if compute_value_func is not None:
                value = compute_value_func(
                    row if compute_key is None else row[compute_key])

            if index is None:
                row.append(value)
            else:
                row.insert(index, value)

        if index is None:
            self.row_columns += [column]
            if self.row_columns is not self.columns and \
                            column not in self.columns:
                self.columns.append(column)
        else:
            self.row_columns = self.row_columns[:index] + [column] \
                               + self.row_columns[index:]
            self.columns.insert(index, column)

        self._parameters[column] = list(set(self.get_column(column)))

    def get_column(self, item):
        index = self.columns.index(item)
        return [row[index] for row in self.table]

    def sort_by_key(self, keys=None):
        """
        :param keys: list of str to sort by, if name starts with -
            reverse order
        :return: None
        """
        keys = keys or self.key_on
        keys = keys if isinstance(keys, (list, tuple)) else [keys]
        for key in reversed(keys):
            reverse, key = (True, key[1:]) if key[0] == '-' else (False, key)
            self.table.sort(key=lambda row: row[key], reverse=reverse)

    def reverse(self):
        self.table.reverse()

    @staticmethod
    def _get_column_widths(list_of_list, min_width=2, max_width=300,
                           padding=1, pad_last_column=False):
        def _len(text):
            if len(text) > 15:
                pass
            if sys.version[0] == 2 and isinstance(text, unicode):
                if u'\n' in text:
                    return len(text.split(u'\n', 1)[0])
            elif '\n' in text:
                return len(text.split('\n', 1)[0])
            return len(text)

        widths = []
        for col in range(len(list_of_list[0])):
            width = max([_len(row[col]) + padding for row in list_of_list])
            widths.append(max(min_width, min(max_width, width)))
        if not pad_last_column and widths:
            widths[-1] = 0
        return widths

    @classmethod
    def _safe_str(cls, cell, quote_numbers=True, repr_line_break=False):
        """
        :param cell: obj to turn in to a string
        :param quote_numbers: if True numbers will be quoted
        :param repr_line_break: if True will replace \n with \\n"""
        if cell is None:
            return ''

        ret = str(cell) if not isinstance(cell, BASESTRING) else cell
        if quote_numbers and isinstance(cell, BASESTRING):
            if (ret.replace(u'.', u'').isdigit() or
                        u'"' in ret or ret in [u'False', u'True']):
                ret = u'"%s"' % ret

        if repr_line_break:
            ret = ret.replace(u'\n', u'\\n')
        return ret

    @classmethod
    def _excel_cell(cls, cell, quote_everything=False):
        """
        This will return a text that excel interprets correctly when
        importing csv
        :param cell: obj to store in the cell
        :param quote_everything: bool to quote even if not necessary
        :return: str
        """
        if cell is None:
            return u''
        if cell is True:
            return u'TRUE'
        if cell is False:
            return u'FALSE'

        ret = cell if isinstance(cell, BASESTRING) else UNICODE(cell)
        if isinstance(cell, (int, float)) and not quote_everything:
            return ret

        ret = ret.replace(u'\u2019', u"'").replace(u'\u2018', u"'")
        ret = ret.replace(u'\u201c', u'"').replace(u'\u201d', u'"')
        ret = ret.replace(u'\r', u'\\r')
        ret = ret.replace(u'\n', u'\r')
        ret = ret.replace(u'"', u'""')

        if (ret.replace(u'.', u'').isdigit() or
                ret.startswith(u' ') or ret.endswith(u' ')):
            return u'"%s"' % ret

        for special_char in [u'\r', u'\t', u'"', u',', u"'"]:
            if special_char in ret:
                return u'"%s"' % ret

        return ret

    @staticmethod
    def _eval_cell(cell, quote_replacement=False):
        cell = cell.strip()
        if cell and cell[0] == '"' and cell[-1] == '"':
            cell = cell[1:-1]
        if quote_replacement:
            cell = cell.replace('""', '"')
        if cell.replace('.', '').isdigit():
            while cell.startswith('0') and cell != '0':
                cell = cell[1:]
            cell = eval(cell)
        return cell

    @staticmethod
    def _clean_cell(text):
        text = text.strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        elif text.replace('.', '').isdigit() or text in ['True', 'False']:
            text = eval(text)
        return text

    @staticmethod
    def _create_column_index(row_columns):
        return OrderedDict(
            [(col, index) for index, col in enumerate(row_columns)])

    @classmethod
    def _get_normalized_columns(cls, list_):
        """
        :param list_: list of dict
        :return: list of string of every key in all the dictionaries
        """
        ret = []
        for row in list_:
            if len(row.keys()) > len(ret):
                ret = cls._ordered_keys(row)

        for row in list_:
            for key in row.keys():
                if key not in ret:
                    ret.append(key)
                    if not isinstance(row, OrderedDict):
                        ret.sort()
        return ret

    @staticmethod
    def _ordered_keys(dict_):
        """
        :param dict_: dict of OrderedDict to be processed
        :return: list of str of keys in the original order
            or in alphabetical order
        """
        return isinstance(dict_, OrderedDict) and dict_.keys() or \
               dict_ and sorted(dict_.keys()) or []

    @staticmethod
    def _key_on_columns(key_on, columns):
        """
        :param key_on: str of column
        :param columns: list of str of columns
        :return: list of str with the key_on in the front of the list
        """
        if key_on is not None:
            if key_on in columns:
                columns.remove(key_on)
            columns = [key_on] + columns
        return columns

    @staticmethod
    def _title_column(name):
        return " ".join([word.title() for word in str(name).split('_')])

    @staticmethod
    def _underscore_column(name):
        return name.lower().replace(' ', '_')

    @staticmethod
    def _index_iterator(column_size, max_size, mix_index=False):
        """
            This will iterate over the indexes and return a list of indexes
        :param column_size: list of int of the size of each list
        :param max_size: int of the max number of iterations
        :param mix_index: bool if True will go first then last then middle
        :return: list of int of indexes
        """
        # todo implement a proper partial factorial design
        indexes = [0] * len(column_size)

        index_order = [0]
        if mix_index:
            for i in range(1, max(column_size)):
                index_order += [-1 * i, i]
        else:
            index_order += range(1, max(column_size))

        for i in range(max_size):
            yield [index_order[indexes[i]] for i in range(len(indexes))]

            for index in range(len(column_size)):
                indexes[index] += 1
                if indexes[index] < column_size[index]:
                    break

                indexes[index] = 0
                if index == len(column_size) - 1:
                    if sys.version_info[0] == 2:
                        raise StopIteration()
                    else:
                        return

    @classmethod
    def _save_file(cls, file_path, text):
        if file_path is None:
            return
        if isinstance(text, UNICODE):
            text = text.encode(cls.ENCODING)
        with open(file_path, 'wb') as fp:
            fp.write(text)

    @classmethod
    def _html_cell(cls, cell):
        head = '<th'
        if isinstance(cell, HTMLRowRespan):
            if cell.count == 0:
                return ''
            head = '<th rowspan="%s"' % cell.count

        if cell is None:
            return '%s/>' % head
        if '\n' not in cls._safe_str(cell):
            return '%s>%s</th>' % (head, cell)
        return '%s align="left">%s</th>' % (
            head, cls._safe_str(cell).replace('\n', '<br>'))

    def _html_link_cells(self):
        """
        This will return a new table with cell linked with their columns
        that have <Link> in the name
        :return:
        """
        new_table = self.copy()
        for row in new_table:
            for c in new_table.columns:
                link = '%s <Link>' % c
                if row.get(link, None):
                    row[c] = '<a href="%s">%s</a>' % (row[link], row[c])

        new_table.columns = [c for c in self.columns if '<Link>' not in c]
        return new_table

    def _html_row_respan(self, row_span):
        row_span = [col for col in (row_span or []) if col in self.columns]
        if not row_span or len(self) < 2:
            return
        i = 0
        while i < len(self):
            for j, row in enumerate(self[i + 1:], i + 1):
                differences = [c for c in row_span if self[i][c] != row[c]]
                if differences:
                    break
                for c in row_span:
                    self[i][c] = HTMLRowRespan(row[c], j - i + 1)
                    row[c] = HTMLRowRespan(row[c])
            i = j if i != j else i + 1

    def _html_row(self, row, tab='  ', background_color=None, header='',
                  align='center'):
        data = [self._html_cell(cell) for cell in row]

        if background_color is not None:
            header = 'bgcolor="%s"' % background_color + header

        header += 'align="%s"' % align
        return '<tr %s>\n%s  %s\n%s</tr>' % (
            header, tab, ('\n%s  ' % tab).join(data), tab)

    def _pertibate_value(self, index, column):
        # noinspection PyTypeChecker
        value = self._parameters.get(column, '')
        if isinstance(value, list):
            return value[index]
        return value

    def _column_width(self, index=None, name=None, max_width=300, **kwargs):
        """
        :param index: int of the column index
        :param name: str of the name of the column
        :param max_width: int of the max size of characters in the width
        :return: int of the width of this column
        """
        assert name is not None or index is not None
        if name and name not in self._column_index:
            return min(max_width, name)

        if index is not None:
            name = self.columns[index]
        else:
            index = self._column_index[name]

        values_width = [len(name)]
        if isinstance(self._parameters.get(name, None), list):
            values_width += [len(self._safe_str(p, **kwargs))
                             for p in self._parameters[name]]

        values_width += [len(self._safe_str(row[index], **kwargs))
                         for row in self.table]

        ret = max(values_width)
        return min(max_width, ret) if max_width else ret

    def _normalize_row(self, row):
        if row is None:
            values = [None] * len(self.row_columns)
        elif isinstance(row, (dict, SeabornRow)):
            values = [row.get(k, None) for k in self.row_columns]
        elif not isinstance(row, list):
            values = [getattr(row, k, None) for k in self.row_columns]
        else:
            values = row + [None] * (len(row) - len(self.row_columns))
        return SeabornRow(self._column_index, values)


class SeabornRow(list):
    def __init__(self, column_index, values):
        super(SeabornRow, self).__init__(
            values + [None] * (len(column_index) - len(values)))
        self.column_index = column_index

    def __getitem__(self, item):
        if isinstance(item, int):
            return list.__getitem__(self, item)
        else:
            return list.__getitem__(self, self.column_index[item])

    def __setitem__(self, item, value):
        if isinstance(item, int):
            return list.__setitem__(self, item, value)
        else:
            return list.__setitem__(self, self.column_index[item], value)

    @property
    def columns(self):
        return self.column_index.keys()

    def __repr__(self):
        return super(SeabornRow, self).__repr__()

    def __str__(self):
        return super(SeabornRow, self).__str__()

    def obj_to_dict(self):
        return {col: list.__getitem__(self, i)
                for col, i in self.column_index.items()}

    def get(self, key, default=None):
        index = self.column_index.get(key, None)
        key = index if index is not None else key
        if isinstance(key, int) and key < len(self):
            return list.__getitem__(self, key)
        else:
            return default

    def update(self, dict_):
        """
            This will update the row values if the columns exist
        :param dict_: dict of values to update
        :return: None
        """
        for key, value in dict_.items():
            index = self.column_index.get(key, None)
            if index is not None:
                list.__setitem__(self, index, value)

    def copy(self):
        return SeabornRow(self.column_index, list(self) + [])

    def append(self, value):
        list.append(self, value)

    def __nonzero__(self):
        for cell in self:
            if cell:
                return True
        return False


class HTMLRowRespan(object):
    def __init__(self, value, count=0):
        self.value = value
        self.count = count

    def __str__(self):
        return '' if self.value is None else str(self.value)

    def __cmp__(self, other):
        return self.value != other


BASESTRING = basestring if sys.version_info[0] == 2 else str
UNICODE = unicode if sys.version_info[0] == 2 else str


def main(source=None, destination=None):
    if source is None and len(sys.argv) != 3:
        print(globals()['__doc__'])
        return
    source = sys.argv[1] if source is None else source
    destination = sys.argv[2] if destination is None else destination
    table = SeabornTable.file_to_obj(source)
    table.obj_to_file(destination)


if __name__ == '__main__':
    main()
