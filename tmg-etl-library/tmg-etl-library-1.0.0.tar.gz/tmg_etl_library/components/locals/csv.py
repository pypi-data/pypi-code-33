from tmg_etl_library.components.locals.local import Local


class CSVClient(Local):
    def __init__(self, log):
        super().__init__(log)

    def read_file(self):
        pass

    def delete_file(self):
        pass

    def insert_data(self):
        pass


class CSVFile:
    #TODO: Discuss, is it better to have one parameter for the full path?
    def __init__(self, name, path, delimiter, quote_char=None):
        self.name = name
        self.path = path
        self.delimiter = delimiter
        self.quote_char = quote_char
        self.full_path = '%s/%s' % (self.path, self.name)
