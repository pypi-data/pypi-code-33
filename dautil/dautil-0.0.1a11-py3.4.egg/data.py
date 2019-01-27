import pandas as pd
import requests
from io import BytesIO
import zipfile
from appdirs import AppDirs
import os
from pkg_resources import resource_filename


def process_zip(url, path, fname):
    response = requests.get(url)
    zip = zipfile.ZipFile(BytesIO(response.content))

    return zip.extract(fname, path)

def get_data_dir():
    dirs = AppDirs("PythonDataAnalysisCookbook", "Ivan Idris")
    path = dirs.user_data_dir
    print(path)

    if not os.path.exists(path):
        os.mkdir(path)

    return path

class Weather():
    @staticmethod
    def load():
        pckl = resource_filename(__name__, 'weather.pckl')
        return pd.read_pickle(pckl)

    @staticmethod
    def fetch_DeBilt_weather():
        url = 'http://www.knmi.nl/klimatologie/daggegevens/datafiles3/260/etmgeg_260.zip'
        path = get_data_dir()
        file = process_zip(url, path, 'etmgeg_260.txt')
        df = pd.read_csv(file,
             skiprows=47,
             usecols=['YYYYMMDD', 'DDVEC', '   FG', '   TG', '   RH', '   PG'], 
             index_col=0, parse_dates=True, na_values='     ')

        df.columns = ['WIND_DIR', 'WIND_SPEED', 'TEMP', 'RAIN', 'PRESSURE']
        df[df['RAIN'] == -1] = 0.05/2
        df['WIND_SPEED'] = 0.1 * df['WIND_SPEED']
        df['TEMP'] = 0.1 * df['TEMP']
        df['RAIN'] = 0.1 * df['RAIN']
        df['PRESSURE'] = 0.1 * df['PRESSURE']
        print(df.index[-1])

        pckl = os.path.join(path, 'weather.pckl')
        df.to_pickle(pckl)
        assert df.equals(pd.read_pickle(pckl))
