import xlsxwriter
from snucovery.errors import InvalidWorksheetName, WorksheetNotExists


class ExcelWorkbooks:
    def __init__(self, workbook_name):
        """Create Excel Workbooks with tabbed sheets

        Full Excel workbook with formatted sheets similar subject data

        Args:
            workbook_name (str): Desired filename of the workbook to be created

        Self:
            workbook_name (str): Valid xlsx filename, `workbook_name`.xlsx
            workbook (obj): xlsxwriter.Workbook() object.
            worksheets (dict): Dict of worksheets to be created in the workbook
        """
        self.workbook_name = self.get_workbook_name(workbook_name)
        self.workbook = self.get_workbook()
        self.worksheets = dict()

    def create_workbook(self, workbook_name=None):
        """Instantiate a new Workbook to work on

        This creates the parent workbook that will be used for generating the
        workbook object.

        Args:
            workbook_name (str) Optional: Specify a new workbook name or fall
                                back on self.workbook_name

        Returns:
            Object :: xlsxwriter.Workbook()
        """
        if not workbook_name:
            workbook_name = self.workbook_name
        self.workbook = xlsxwriter.Workbook(self.get_workbook_name(workbook_name))
        return self.workbook

    def create_worksheet(self, worksheet_name):
        """Create a new worksheet with a specified worksheet_name

        When a new worksheet is created, it automatically adds it to the
        worksheets dict by calling self.add_new_worksheet().

        Args:
            worksheet_name (str): name of the worksheet to be created and added
                                  to the workbook

        Returns:
            Object
        """
        if not worksheet_name:
            raise InvalidWorksheetName
        worksheet = self.get_workbook().add_worksheet(worksheet_name.title())
        self.add_new_worksheet(worksheet_name, worksheet)
        return worksheet

    def add_new_worksheet(self, worksheet_name, worksheet):
        """Update self.worksheets dict with the worksheet name and object

        Args:
            worksheet_name (str): name of the worksheet
            worksheet (obj): worksheet object to associate with the name

        Returns:
            Object :: worksheet object
        """
        self.worksheets.update({
            worksheet_name: worksheet
        })
        return worksheet

    def set_workbook_name(self, workbook_name):
        """Returns a valid workbook name with the proper extension

        This will take `filename` or `filename.xlsx` and return a valid
        filename that contains the `.xlsx` file extension

        Args:
            workbook_name (str): workbook name

        Returns:
            String :: Valid filename for the excel workbook
        """
        if not '.xlsx' in workbook_name[-5:]:
            workbook_name = f"{workbook_name}.xlsx"
        return workbook_name

    def get_workbook_name(self, workbook_name):
        """Reurns a valid workbook filename

        This might need to be reworked.
        Attempts to return self.workbook_name but if it doesnt exist, it will
        set the name based on the passed `workbook_name`

        Args:
            workbook_name (str): workbook name

        Returns:
            String :: Valid filename for the excel workbook
        """
        try:
            if not workbook_name:
                return self.workbook_name
        except AttributeError:
            pass
        self.workbook_name = self.set_workbook_name(workbook_name)
        return self.workbook_name

    def get_workbook(self):
        """Returns the current workbook or creates a new one if not exists

        Try and return the current instantiated workbook, if it doesnt exist,
        it will create a new workbook based on the instantiated `workbook_name`

        Returns:
            Object :: workbook object
        """
        try:
            return self.workbook
        except AttributeError:
            return self.create_workbook()

    def get_worksheets(self):
        """Return worksheets dict

        Returns:
            Dict :: dict of all created worksheets
        """
        return self.worksheets

    def get_worksheet(self, worksheet_name):
        """Return a worksheet by name if it exists or raise exception

        Args:
            worksheet_name (str): worksheet name to return

        Returns:
            Try to return the worksheet if it exists or raise exception for
            WorksheetNotExists
        """
        worksheets = self.get_worksheets()
        if worksheet_name in worksheets:
            return worksheets[worksheet_name]
        raise WorksheetNotExists

    def set_header_formatting(self):
        """Returns bold formatting for headers

        Bolden the headers of the workbook

        Returns:
            Object :: workbook.add_format()
        """
        return self.get_workbook().add_format({'bold': True})

    def create_header(self, worksheet_name, header, col, width, sort=True):
        """Create a header in a specific column on row 0 and set col width

        This creates a header on the first row of a worksheet.  It also sets
        the width of the column and if `sort` is True, make the columns
        sortable.

        Args:
            worksheet_name (str): name of the worksheet to add the header to
            header (str): string to set the cell text to for the header
            col (int): which column to add the header to
            width (int): width of the column
            sort (bool) default=True: Make columns sortable
        """
        worksheet = self.get_worksheet(worksheet_name)
        worksheet.set_column(col, col, width)
        worksheet.write(0, col, header, self.set_header_formatting())
        if sort:
            worksheet.autofilter(0, 0, 0, col)

    def create_headers_from_dict(self, worksheet_name, header_dict):
        """Create all headers for a worksheet based on a dict

        This iterates through the dictionary and sets a key for the cell header
        and creates a width based on the key or value, depending on what the
        value is.

        Args:
            worksheet_name (str): name of the worksheet to create the headers
                                  on
            header_dict (dict): key: value dict where the key is the header
        """
        col = 0
        for key, value in header_dict.items():
            width = self.get_header_width(key, value)
            self.create_header(worksheet_name, key, col, width)
            col += 1

    def get_header_width(self, key, value):
        """Get the width of the header based on the key or the value

        The width of the header gets set based on key if a value isnt set. If
        a value exists, it will set the width to +10 of the value width.  If
        value is a list(), it will set the width to twice the width of a string
        plus 10.

        Args:
            key (str): key of the headers
            value (str or list): value

        Returns:
            Int :: width to set the header to
        """
        width = len(key) + 10
        if value:
            width = len(value) + 10
            if isinstance(value, list):
                value = ', '.join(value)
                width = len(value) + (len(value) * 2) + 10
        return width

    def add_row_to_worksheet(self, worksheet, row_data, row_counter):
        """Add a new row to the worksheet

        Iterate through a row of data in dict format and starting at col == 0,
        increment through the items and place the value in the specified cell

        Args:
            worksheet (str): name of a valid worksheet
            row_data (dict): dictionary of key: values where the key is the
                             header and the value is contents
        """
        col_counter = 0
        for value in row_data.values():
            if isinstance(value, list):
                value = ", ".join(value)
            worksheet.write(row_counter, col_counter, value)
            col_counter += 1

    def add_rows_to_worksheet_from_json(self, worksheet_name, worksheet_data):
        """Take a JSON doc and fill a worksheet with the data

        Pass a dictionary and iterate through it to fill the desired worksheet

        Args:
            worksheet_name (str): valid worksheet name
            worksheet_data (dict): dictionary or json doc to iterate through
        """
        worksheet = self.get_worksheet(worksheet_name)
        row_counter = 1
        for row_data in worksheet_data:
            self.add_row_to_worksheet(worksheet, row_data, row_counter)
            row_counter += 1

    def close(self):
        """Close the workbook to save the file"""
        self.get_workbook().close()
