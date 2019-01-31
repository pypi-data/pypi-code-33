from StringIO import StringIO
from zipfile import ZipFile
from urllib import urlopen


def download_and_read(country_code):
    return ZipFile(StringIO(urlopen(
        'http://download.geonames.org/export/dump/{}.zip'
        .format(country_code.upper())
    ).read())).open(country_code.upper() + '.txt').readlines()
