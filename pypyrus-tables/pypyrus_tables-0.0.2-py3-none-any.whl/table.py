from .parser import parse_name

# Class to work with text tables.
# Object of that class will hold in attributes different table presentations:
# LINES - tuple of strings where one string is a table row;
# ROWS - tuple of tuples where items in nested tuples are cells of a table row;
# COLUMNS - tuple of tuples where items in nested tuple are cells of a table
# column;
# DATA - dictionary where items are the tables field name and tuple with it
# values.
# Each presentation is a part of chain: LINES -> ROWS -> COLUMNS -> DATA.
# So we can say that LINES is the lowest table presentation and DATA is the
# highest table presentation.
class Table():
    def __init__(self, path = None, sep = '\t', head = True,
        lines = None, rows = None, columns = None, data = None,
        ):
        self.__path = path
        self.__sep = sep
        self.__head = head

        # Initiate all table presentations.
        self.__lines = lines
        self.__rows = rows
        self.__columns = columns
        self.__data = data
        # In presentations there are two critical points: a LINES as the lowest
        # and a DATA as the highest. If one of them is empty then parse other
        # presentatoins to get it. If other presentations are also missing they
        # will be parsed because dependecies are created internally in parsing
        # methods.
        if self.__data is None: self.parse_columns()
        if self.__lines is None: self.parse_to_lines()

        # Calculate table parameters.
        self.__count_cols = len(self.__data)
        self.__count_rows = max([len(value) for value in self.__data.values()])
        pass

    def __getattr__(self, name):
        try:
            return self.__data[name]
        except KeyError:
            raise AttributeError(f'can not find attribute {name}.')

    def __getitem__(self, key):
        if isinstance(key, str) is True:
            try:
                return self.__data[key]
            except KeyError:
                raise KeyError(f'incorrect key {key}')
        elif isinstance(key, int) is True:
            try:
                data = dict()
                for name in self.__data.keys():
                    data[name] = (self.__data[name][key], )
                return Table(data = data)
            except IndexError:
                raise IndexError(f'incorrect index {key}.')
        else:
            raise TypeError('incorrect data type. Key must be integer or string.')

    def __str__(self):
        return self.show()

    @property
    def PATH(self):
        return self.__path

    @property
    def LINES(self):
        return self.__lines

    @property
    def ROWS(self):
        return self.__rows

    @property
    def DATA(self):
        return self.__data

    @property
    def COLUMNS(self):
        return self.__columns

    @property
    def COUNT_COLS(self):
        return self.__count_cols

    @property
    def COUNT_ROWS(self):
        return self.__count_rows

    # Parse file to lines of lines.
    def parse_file(self):
        if self.__lines is None:
            path = self.__path
            self.__lines = open(path, 'r').readlines()
        return self.__lines

    # Parse list of lines to list of raws.
    def parse_lines(self):
        if self.__rows is None:
            lines = self.__lines or self.parse_file()
            sep = self.__sep

            self.__rows = tuple([tuple(line.replace('\n', '').split(sep)) for line in lines])
        return self.__rows

    # Parse list of rows to list of fields.
    def parse_rows(self):
        if self.__columns is None:
            rows = self.__rows or self.parse_lines()

            self.__columns = tuple(zip(*rows))
        return self.__columns

    # Parse list of fields to dictionary of fields.
    def parse_columns(self):
        columns = self.__columns or self.parse_rows()
        head = self.__head

        # Define list with fields names.
        names = [parse_name(column[0] if head is True else i) for i, column in enumerate(columns)]
        # Define list with fields values.
        values = [column[1:] if head is True else column for column in columns]
        # Zip them together and convert to dict.

        self.__data = dict(zip(names, values))
        return self.__data

    # Parse dictionary of fields to list of fields.
    def parse_to_columns(self):
        if self.__columns is None:
            data = self.__data or self.parse_columns()

            # Unite fields names and fields values to one list where names
            # is a first item in list.
            self.__columns = tuple([(key, *value) for key, value in data.items()])
        return self.__columns

    # Parse list of fields to list of rows.
    def parse_to_rows(self):
        if self.__rows is None:
            columns = self.__columns or self.parse_to_columns()
            # All items in fields with same index becomes separate list.
            self.__rows = tuple(zip(*columns))
        return self.__rows

    # Parse list of rows to list of lines.
    def parse_to_lines(self):
        if self.__lines is None:
            rows = self.__rows or self.parse_to_rows()
            sep = self.__sep

            self.__lines = [f'{sep.join(row)}\n' for row in rows]
        return self.__lines

    # Parse list of rows to forammted string.
    def parse_to_string(self):
        rows = self.__rows
        columns = self.__columns
        head = self.__head

        # List of fixed lengths for each field in same order.
        lengths = [max([len(cell) for cell in column]) + 1 for column in columns]
        # Total length of one row in string.
        length = sum(lengths) + len(columns) + 1
        # Horizontal border.
        border = f'{str():-^{length}}\n'

        # Must begin from a horizontal line.
        string = border
        for i_row, row in enumerate(rows):
            # Each string must begin from a vertical border.
            string += '|'
            for i_cell, cell in enumerate(row):
                # Select fixed length for current field.
                l_cell = lengths[i_cell]
                string += f'{cell:<{l_cell}}|'
            # Each line must end with a new line.
            string += '\n'
            # If header is enabled then end first line with a horizontal border.
            if i_row == 0 and head is True:
                string += border
        # Must end with a horizontal line.
        string += border

        return string

    # Present data as formatted text table.
    def show(self):
        return self.parse_to_string()

    # Output the table to the file.
    def write(self, path):
        with open(path, 'w') as output_file:
            output = ''.join(self.__lines)
            output_file.write(output)
        pass

    # Find indexes of records by parameters in kwargs.
    def find(self, **kwargs):
        matches = dict()
        for key, value in kwargs.items():
            matches[key] = list()
            for i, data_value in enumerate(self.__data[key]):
                if type(value).__name__ in ('list', 'tuple', 'set', 'frozenset'):
                    if data_value in value:
                        matches[key].append(i)
                else:
                    if data_value == str(value):
                        matches[key].append(i)
        return matches

    # Select records from table that correspond to some parameters.
    # Result is a new Table object.
    def select(self, **kwargs):
        # Get indexes of cells in DATA values where value is found.
        matches = list(self.find(**kwargs).values())
        # Intersect indexes to avoid conflicts if there were multiple parameters.
        matches = set(matches[0]).intersection(*matches[1:])
        # Consider the header.
        if self.__head is True:
            matches = set(map(lambda i: i + 1, matches))
        rows = [self.__rows[0]] if self.__head is True else []
        for i, row in enumerate(self.__rows):
            # Pick only rows that are matched.
            if i in matches:
                rows.append(row)
        return Table(rows = rows)

    # Filter records from table that correspond to some parameters.
    # Result is a new Table object.
    def filter(self, **kwargs):
        # Get indexes of cells in DATA values where value is found.
        matches = list(self.find(**kwargs).values())
        # Intersect indexes to avoid conflicts if there were multiple parameters.
        matches = set(matches[0]).intersection(*matches[1:])
        # Consider the header.
        if self.__head is True:
            matches = set(map(lambda i: i + 1, matches))
        rows = [self.__rows[0]] if self.__head is True else []
        for i, row in enumerate(self.__rows):
            # Pick only rows that are not matched.
            if i not in matches:
                # Consider the header.
                if self.__head is True and i == 0:
                    continue
                rows.append(row)
        return Table(rows = rows)
