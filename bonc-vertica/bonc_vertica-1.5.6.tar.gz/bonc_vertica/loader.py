import csv
import codecs
from bonc_vertica.settings import logging


class DataLoader(object):
    """
    负责将数据写入文件
    """
    def __init__(self, file=None, iter_rows=None, encoding=None, delimiter=None, quotechar=None, quoting=None):
        self.file = file
        self.iter_rows = iter_rows if iter_rows else []
        self.encoding = encoding if encoding else 'utf8'
        self.delimiter = delimiter if delimiter else ','
        self.quotechar = quotechar if quotechar else '"'
        self.quoting = quoting if quoting else csv.QUOTE_ALL
        self.writen_count = 0
        self.outport_count = 0
        self.width = 0

    def row_to_line(self, row):
        quotechar = self.quotechar if self.quoting else ''
        line = self.delimiter.join(['{quotechar}{ele}{quotechar}'.format(quotechar=quotechar, ele=e) for e in row])
        return line.encode(self.encoding, 'ignore')

    def write_csv_content(self, content):
        with codecs.open(self.file, mode='ab+') as f:
            f.write(content)

    def get_save_as_file(self, file):
        self.file = file
        return self

    def overwrite_iter_rows(self, iter_rows):
        self.iter_rows = iter_rows
        return self

    def load_to_csv(self):
        i = 0
        content = b''
        for row in self.iter_rows:
            i += 1
            self.outport_count += 1
            if any(row):
                self.writen_count += 1
                content += self.row_to_line(row) + b'\n'
                if i >= 10000:
                    self.write_csv_content(content)
                    logging.info('已导出 {} 行'.format(self.outport_count))

                    i = 0
                    content = b''
            else:
                logging.warning('存在全为空的行！line: {}\n\t此行不会被写入'.format(self.outport_count))

        self.width = len(row)

        if content:
            self.write_csv_content(content)

