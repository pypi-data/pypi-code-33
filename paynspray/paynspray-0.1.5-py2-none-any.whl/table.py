import copy, csv, ipaddress, os, re
# Python 2/3 switch
try:
    from itertools import izip_longest
except ImportError:
    from itertools import zip_longest as izip_longest

class Table(object):
    """Class used to pretty-print text in a tabular format"""
    def __init__(self, **kwargs):
        """
        Initializes a text table instance using provided arguments.
        
        Args:
            Header (str): The text to display above the table.  Default: None (no header)
            HeaderIndent (int): The number of spaces to indent the header.  Default: 0
            Columns (list): The list of columns to use in the table.
            Rows (list): The list of rows to use in the table.
            Width (int): The maximum character width of the table.  Default: 80
            Indent (int): The number of spaces to indent the table.  Default: 0
            CellPad (int): The number of spaces between each horizontal cell.  Default: 2
            Prefix (str): The text to display before the table.
            Postfix (str): The text to display after the table.
            SearchTerm (str): The regular expression used to filter rows.
            SortIndex (int): The column index used to sort the table.  -1 disables sorting.  Default: 0
            SortOrder (str): The direction in which to sort the table.  Default: 'forward'
        """
        if 'Header' in kwargs:
            self.header = kwargs['Header']
        else:
            self.header = None
            
        if 'HeaderIndent' in kwargs:
            self.headeri = kwargs['HeaderIndent']
        else:
            self.headeri = 0
        
        if 'Columns' in kwargs:
            self.columns = kwargs['Columns']
        else:
            self.columns = []
            
        self.rows = []
        
        if 'Width' in kwargs:
            self.width = kwargs['Width']
        else:
            self.width = 80
            
        if 'Indent' in kwargs:
            self.indent = kwargs['Indent']
        else:
            self.indent = 0
            
        if 'CellPad' in kwargs:
            self.cellpad = kwargs['CellPad']
        else:
            self.cellpad = 2
            
        if 'Prefix' in kwargs:
            self.prefix = kwargs['Prefix']
        else:
            self.prefix = ''
            
        if 'Postfix' in kwargs:
            self.postfix = kwargs['Postfix']
        else:
            self.postfix = ''
            
        self.colprops = []
        
        if 'SearchTerm' in kwargs:
            self.scterm = r'{}'.format(kwargs['SearchTerm'])
        else:
            self.scterm = None
            
        if 'SortIndex' in kwargs:
            self.sort_index = kwargs['SortIndex']
        else:
            self.sort_index = 0
            
        if 'SortOrder' in kwargs:
            self.sort_order = kwargs['SortOrder']
        else:
            self.sort_order = 'forward'
            
        for idx in range(0, len(self.columns)):
            self.colprops.append({})
            self.colprops[idx]['MaxWidth'] = len(self.columns[idx])
            
        if 'Rows' in kwargs:
            for row in kwargs['Rows']:
                self.add_row(row)
                
        if 'ColProps' in kwargs:
            for col in kwargs['ColProps']:
                try:
                    idx = self.columns.index(col)
                    self.colprops[idx].update(kwargs['ColProps'][col])
                except ValueError:
                    pass
                
            
    def add_row(self, fields = []):
        if len(fields) != len(self.columns):
            raise RuntimeError("Invalid number of columns!")
        
        for idx, field in enumerate(fields):
            field = str(field).strip()
            if self.colprops[idx]['MaxWidth'] < len(str(field)):
                old = self.colprops[idx]['MaxWidth']
                self.colprops[idx]['MaxWidth'] = len(str(field))
            
        self.rows.append(fields)
        
    def add_hr(self):
        self.rows.append('__hr__')
        
    @classmethod
    def ip_cmp(self, a, b):
        """Comparison operator used for IP addresses"""
        try:
            a = ipaddress.ip_address(unicode(str(a)))
            b = ipaddress.ip_address(unicode(str(b)))
            
            if a.version == 6 and b.version == 4:
                return 1
            elif a.version == 4 and b.version == 6:
                return -1
                
            if a < b:
                return -1
            elif a == b:
                return 0
            elif a > b:
                return 1
            else:
                return None
            
        except ipaddress.AddressValueError:
            return None
        except ValueError:
            return None

    def sort_rows(self, index = None, order = None):
        if index is None:
            index = self.sort_index
        if order is None:
            order = self.sort_order

        if index == -1:
            return

        if self.rows is None or len(self.rows) == 0:
            return

        def sort_block(a, b):
            try:
                a[index]
            except IndexError:
                cmp = -1
            try:
                b[index]
            except IndexError:
                cmp = 1
            if a[index] is None:
                cmp = -1
            elif b[index] is None:
                cmp = 1
            elif (re.search(r'^[0-9]+$', a[index]) is not None) and (re.search(r'^[0-9]+$', b[index]) is not None):
                if int(a[index]) < int(b[index]):
                    cmp = -1
                elif int(a[index]) == int(b[index]):
                    cmp = 0
                elif int(a[index]) > int(b[index]):
                    cmp = 1
                else:
                    cmp = None
            elif (self.ip_cmp(a[index], b[index]) is not None):
                cmp = self.ip_cmp(a[index], b[index])
            else:
                if (a[index]) < (b[index]):
                    cmp = -1
                elif (a[index]) == (b[index]):
                    cmp = 0
                elif (a[index]) > (b[index]):
                    cmp = 1
                else:
                    cmp = None
            if cmp is None:
                cmp = 0
            if order == 'forward':
                return cmp
            else:
                return -cmp

        self.rows = sorted(self.rows, cmp = sort_block)
            
    def valid_ip(self, value):
        try:
            ipaddress.ip_address(unicode(value))
            return True
        except ipaddress.AddressValueError:
            return False
        except ValueError:
            return False
            
    @classmethod
    def from_csv(self, csvobj):
        """Returns a Table instance using CSV data (either from a string or a file)"""
        if type(csvobj) is str:
            # was it a filename or a raw CSV string?
            if os.path.isfile(csvobj) == True:
                csvfile = file(csvobj, 'rb')
                csvobj = list(csv.reader(csvfile))
            else:
                csvobj = list(csv.reader(csvobj.splitlines()))
                
        if csvobj[0] == ["Keys", "Values"]:
            csvobj.pop(0)
            cols = []
            rows = []
            for row in csvobj:
                cols.append(row.pop(0))
                rows.append(row)
            
            tbl = self.__class__(Columns=cols)
            groups = list(izip_longest(*[iter(rows)] * len(cols)))
            for r in groups:
                tbl.add_row(list(r))
                
        else:
            tbl = self.__class__(Columns=csvobj.pop(0))
            while len(csvobj) > 0:
                tbl.add_row(csvobj.pop(0))
                
        return tbl

    def to_csv(self):
        """Converts the table into CSV format"""
        def csv_block(x):
            x = str(x)
            x = re.sub(r'[\r\n]', ' ', x)
            x = re.sub(r'\s+', ' ', x)
            x = re.sub(r'"', '""', x)
            return x

        string = ''
        string += (",".join(self.columns) + "\n")
        for row in self.rows:
            if self.is_hr(row) == True or self.row_visible(row) == False:
                continue
            string += (",".join(map(lambda x: "\"{}\"".format(x), map(lambda x: csv_block(x), row))) + "\n")

        return string   
        
    def __str__(self):
        """Returns string representation of the table"""
        retval = copy.copy(self.prefix)
        retval = retval + self.header_to_str()
        retval = retval + self.columns_to_str()
        retval = retval + self.hr_to_str()
        
        self.sort_rows()
        for row in self.rows:
            if self.is_hr(row) == True:
                retval = retval + self.hr_to_str()
            else:
                if self.row_visible(row):
                    retval = retval + self.row_to_str(row)
                    
        retval = retval + self.postfix
        
        return retval
        
    def header_to_str(self):
        if self.header is not None:
            pad = " " * self.headeri
            return pad + self.header + "\n" + pad + ("=" * len(self.header)) + "\n\n"
        
        return ''
        
    def columns_to_str(self):
        nameline = ' ' * self.indent
        barline = copy.copy(nameline)
        last_col = None
        last_idx = None
        for idx, col in enumerate(self.columns):
            if last_col is not None:
                padding = self.pad(' ', last_col, last_idx)
                nameline = nameline + padding
                remainder = len(padding) - self.cellpad
                if remainder < 0:
                    remainder = 0
                barline = barline + (' ' * (self.cellpad + remainder))
                
            nameline = nameline + col
            barline = barline + ('-' * len(col))
            
            last_col = col
            last_idx = idx
            
        return "{}\n{}".format(nameline, barline)
        
    def hr_to_str(self):
        return "\n"
        
    def row_to_str(self, row):
        line = ' ' * self.indent
        last_cell = None
        last_idx = None
        for idx, cell in enumerate(row):
            if idx != 0:
                line = line + self.pad(' ', str(last_cell), last_idx)
            
            if 'MaxChar' in self.colprops[idx]:
                last_cell = str(cell)[0:(int(self.colprops[idx]['MaxChar']) + 1)]
                line = line + last_cell
            else:
                line = line + str(cell)
                last_cell = cell
                
            last_idx = idx
            
        return line + "\n"
        
    def pad(self, chr, buf, colidx, use_cell_pad = True):
        if 'MaxChar' in self.colprops[colidx]:
            max = self.colprops[colidx]['MaxChar']
        elif 'MaxWidth' in self.colprops[colidx]:
            max = self.colprops[colidx]['MaxWidth']
            
        if int(max) > int(self.colprops[colidx]['MaxWidth']):
            max = self.colprops[colidx]['MaxWidth']
            
        strcpy = str(copy.copy(buf))
        remainder = max - len(strcpy)
        if remainder < 0:
            remainder = 0
            
        val = chr * remainder
        
        if use_cell_pad == True:
            val = val + (' ' * self.cellpad)
            
        return val
        
    def row_visible(self, row):
        if self.scterm is None:
            return True

        return (re.search(self.scterm, self.row_to_str(row)) is not None)
            
    def is_hr(self, row):
        return isinstance(row, str) and (row == '__hr__')
                
    def __getitem__(self, col_names):
        if type(col_names) == str:
            col_names = [col_names]

        tbl = self.__class__(Indent=self.indent,Header=self.header,Columns=col_names)

        indices = []

        for col_name in col_names:
            try:
                index = self.columns.index(col_name)
            except ValueError:
                raise ValueError("Invalid column name '{}'".format(col_name))
            indices.append(index)

        for old_row in self.rows:
            new_row = []
            map(lambda i: new_row.append(old_row[i]), indices)
            tbl.add_row(new_row)

        return tbl

        