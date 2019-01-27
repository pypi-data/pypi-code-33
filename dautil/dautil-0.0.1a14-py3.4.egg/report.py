import pandas as pd
from landslide.generator import Generator as LandslideGenerator
from dautil import data
from dautil import log_api
import os


class DFBuilder():
    def __init__(self, cols, *args):
        self.columns = cols
        self.df = {}

        for col in self.columns:
            self.df.update({col: []})

        for arg in args:
            self.row(arg)

    def row(self, row):
        assert len(row) == len(self.columns)

        for col, val in zip(self.columns, row):
            self.df[col].append(val)

        return self.df

    def build(self, index=None):
        self.df = pd.DataFrame(self.df)

        if index:
            self.df.index = index

        return self.df


class RSTWriter():
    def __init__(self):
        self.rst = ''

    def h1(self, txt):
        self.rst += txt + '\n'
        self.rst += ('=' * len(txt)) + '\n\n'

    def add(self, txt):
        self.rst += txt

    def divider(self):
        self.rst += '\n\n----\n\n'

    def write(self, fname):
        with open(fname, 'w') as f:
            f.write(self.rst)
            log_api.conf_logger(__name__).warning('Wrote to ' + fname)


class Generator():
    CSS = "https://www.googledrive.com/host/0B8Dd5LtC555uNTJQXzZKdDN4aWc"

    def __init__(self, rst_file, out):
        self.dir = data.get_data_dir()
        self.out_file = os.path.join(self.dir, out)
        self.gen = LandslideGenerator(rst_file, destination_file=self.out_file)

    def add_css(self):
        css = os.path.join(self.dir, 'report.css')
        data.download(self.CSS, css)
        self.gen.add_user_css([css])

    def generate(self):
        self.add_css()
        self.gen.write()

        log_api.conf_logger(__name__).warning(
                'Generated HTML in ' + self.out_file)
