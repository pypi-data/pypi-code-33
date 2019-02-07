from countries.portugal import dre
import logging
from datetime import date

from countries.portugal.data import Reader
from fetcher import Session

logging.basicConfig(level=logging.DEBUG)

# reader = dre.Reader()
# reader.publications(date(2019, 1, 1), date(2019, 2, 1))
# crawler.get_publications_index('2019-02-04')

s = Session()
# index = dre.get_publications_index(s, date(2019, 2, 6))
# print(index)
# for entry in index:
#    publication = dre.get_publication(s, entry[0])
#    print(publication)

# print(dre.get_diploma(s, 119236495))

reader = Reader()
# for publication in reader.get_publications(date(2019, 1, 1), date(2019, 1, 10)):
#     print(publication)

print(reader.get_diploma(117663335))
print()