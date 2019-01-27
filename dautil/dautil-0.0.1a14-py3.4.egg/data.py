import pandas as pd
from pandas.io import wb
import numpy as np
from io import BytesIO
import zipfile
import gzip
from appdirs import AppDirs
import os
from pkg_resources import resource_filename
import urllib.request as urlrequest
from dautil import log_api
from collections import namedtuple
from joblib import Memory


def download(url, out):
    req = urlrequest.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urlrequest.urlopen(req)

    with open(out, 'wb') as f:
        f.write(res.read())
        log_api.conf_logger(__name__).warning('Downloaded ' + f.name)


def process_gzip(url, file_path):
    response = urlrequest.urlopen(url)
    compressed = BytesIO(response.read())
    decompressed = gzip.GzipFile(fileobj=compressed)

    with open(file_path, 'wb') as outfile:
        outfile.write(decompressed.read())


def process_zip(url, path, fname):
    response = urlrequest.urlopen(url)

    zip = zipfile.ZipFile(BytesIO(response.read()))

    return zip.extract(fname, path)


def get_data_dir():
    dirs = AppDirs("PythonDataAnalysisCookbook", "Ivan Idris")
    path = dirs.user_data_dir
    log_api.conf_logger(__name__).warning('Data dir ' + path)

    if not os.path.exists(path):
        os.mkdir(path)

    return path


class Nordpil():

    def __init__(self):
        self.dir = get_data_dir()

    def load_urban_tsv(self):
        fname = os.path.join(self.dir,
                             'urbanareas1_1.tsv')

        if not os.path.exists(fname):
            download('http://nordpil.com/static/downloads/urbanareas1_1.tsv',
                     fname)

        return fname


class SPANFB():

    def __init__(self):
        self.fname = os.path.join(get_data_dir(),
                                  'facebook_combined.txt')

    def load(self):
        if not os.path.exists(self.fname):
            process_gzip(
                'https://snap.stanford.edu/data/facebook_combined.txt.gz',
                self.fname)

        return self.fname


class Weather():

    @staticmethod
    def load():
        pckl = resource_filename(__name__, 'weather.pckl')
        return pd.read_pickle(pckl)

    @staticmethod
    def rain_values():
        return Weather.load()['RAIN'].dropna().values

    @staticmethod
    def get_header(alias):
        mapping = {'WIND_DIR': 'Wind Dir',
                   'WIND_SPEED': 'W Speed, m/s',
                   'TEMP': 'Temp, °C',
                   'RAIN': 'Rain, mm',
                   'PRESSURE': 'Pres, hPa'}

        return mapping.get(alias, 'UNKNOWN')

    @staticmethod
    def fetch_DeBilt_weather():
        url = 'http://www.knmi.nl/klimatologie/daggegevens/datafiles3/260/etmgeg_260.zip'
        path = get_data_dir()
        file = process_zip(url, path, 'etmgeg_260.txt')
        df = pd.read_csv(
            file,
            skiprows=47,
            usecols=[
                'YYYYMMDD',
                'DDVEC',
                '   FG',
                '   TG',
                '   RH',
                '   PG'],
            index_col=0,
            parse_dates=True,
            na_values='     ')

        df.columns = ['WIND_DIR', 'WIND_SPEED', 'TEMP', 'RAIN', 'PRESSURE']
        df[df['RAIN'] == -1] = 0.05/2
        df['WIND_SPEED'] = 0.1 * df['WIND_SPEED']
        df['TEMP'] = 0.1 * df['TEMP']
        df['RAIN'] = 0.1 * df['RAIN']
        df[df['PRESSURE'] < 1] = np.nan
        df['PRESSURE'] = 0.1 * df['PRESSURE']
        log_api.conf_logger(__name__).warning(df.index[-1])

        pckl = os.path.join(path, 'weather.pckl')
        df.to_pickle(pckl)
        assert df.equals(pd.read_pickle(pckl))


class Worldbank():
    def __init__(self):
        # TODO make this configurable
        Indicator = namedtuple('Indicator', ['alias', 'name', 'longname'])
        self.indicators = [Indicator(alias='pop_grow', name='sp.pop.grow',
                                     longname='Population Growth'),
                           Indicator(alias='gdp_pcap', name='ny.gdp.pcap.cd',
                                     longname='GDP Per Capita'),
                           Indicator(alias='primary_education',
                                     name='se.prm.cmpt.zs', longname='Primary\
                                     Education Completion Rate')]
        self.alias2name = {i.alias: i.name for i in self.indicators}
        self.name2alias = {j: i for i, j in self.alias2name.items()}
        self.name2longname = {i.name: i.longname for i in self.indicators}
        self.aliases = self.alias2name.keys()
        self.names = self.alias2name.values()

        # caching
        memory = Memory(cachedir='.')
        self.download = memory.cache(self.download)
        self.get_countries = memory.cache(self.get_countries)

    def get_countries(self, *args, **kwargs):
        return wb.get_countries(*args, **kwargs)

    def download(self, *args, **kwargs):
        return wb.download(*args, **kwargs)

    def get_alias(self, name):
        assert name in self.names, self.indicators

        return self.name2alias[name]

    def get_name(self, alias):
        assert alias in self.aliases, self.indicators

        return self.alias2name[alias]

    def get_longname(self, name):
        assert name in self.names, self.indicators

        return self.name2longname[name]

    def rename_columns(self, df, use_longnames=False):
        new_cols = []

        for col in df.columns:
            if use_longnames:
                if col in self.names:
                    new_cols.append(self.name2longname[col])
                else:
                    new_cols.append(col)
            else:
                if col in self.names:
                    new_cols.append(self.name2alias[col])
                else:
                    new_cols.append(col)

        df.columns = new_cols

        return df
