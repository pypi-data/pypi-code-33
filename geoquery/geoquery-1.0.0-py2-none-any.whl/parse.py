import unicodecsv
from geoquery.remote import download_and_read


THRESHOLD = 0.005


def dict_fuzzy_match(d1, d2, fuzzy_keys=set()):
    score = None

    for k, v in d1.items():
        vv = d2.get(k)

        if vv == v:
            return True, score

        if k in fuzzy_keys and vv:
            i = 0
            while i <= THRESHOLD:
                score = 100 - ((i / THRESHOLD) * 100)

                if vv >= (v - i) and vv <= (v + i):
                    return True, score

                i += 0.0001

    return False, score


def typemap(row, types):
    for k in row.iterkeys():
        if k in types:
            row[k] = types[k](row[k])

    return row


def parse_and_query(country_code, query):
    locations = []

    fieldnames = [
        'geonameid',
        'name',
        'asciiname',
        'alternate',
        'latitude',
        'longitude',
        'feature_class',
        'feature_code',
        'country_code',
        'cc2',
        'admin1_code',
        'admin2_code',
        'admin3_code',
        'admin4_code',
        'population',
        'elevation',
        'dem',
        'timezone',
        'modification_date'
    ]

    dtypes = {'latitude': float, 'longitude': float}

    reader = unicodecsv.DictReader(
        download_and_read(country_code),
        fieldnames=fieldnames,
        dialect='excel-tab',
        encoding='utf-8'
    )

    fuzzy_keys = {'latitude', 'longitude'}

    for row in reader:
        row = typemap(row, dtypes)

        does_match, score = dict_fuzzy_match(query, row, fuzzy_keys)

        row['score'] = score

        if does_match:
            locations.append(row)

    return sorted(locations, key=lambda x: x['score'])
