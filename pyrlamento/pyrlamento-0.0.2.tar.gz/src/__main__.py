import logging
from fetcher import Session
from pyrlamento import Pyrlamento

logging.basicConfig(level=logging.DEBUG)

s = Session()

publication = Pyrlamento('countries.portugal').publication(117506449)
print(publication)
