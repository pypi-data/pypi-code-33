import unicodecsv
from geoquery.remote import download_and_read
import math


def typemap(row, types):
    for k in row.iterkeys():
        if k in types:
            row[k] = types[k](row[k])

    return row


def apply_distance(location, lat, lon):
    location['distance'] = math.hypot(
        location['latitude'] - lat, location['longitude'] - lon
    )

    return location


def parse_and_query(country_code, latitude, longitude, distance):
    return sorted(filter(
        lambda l: l['distance'] <= distance,
        [
            apply_distance(
                typemap(r, {'latitude': float, 'longitude': float}),
                latitude,
                longitude
            )

            for r in unicodecsv.DictReader(
                download_and_read(country_code),
                fieldnames=[
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
                ],
                dialect='excel-tab',
                encoding='utf-8'
            )
        ]
    ), key=lambda x: x['distance'], reverse=True)
