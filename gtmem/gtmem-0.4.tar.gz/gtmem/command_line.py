from memair import Memair
from getl import Getl
from optparse import OptionParser
from math import ceil
from time import sleep
import json
import datetime


def main():
  source = "Google Takeout Location History"
  batch_size = 10000
  sleep_time = 5 #seconds

  parser = OptionParser()
  parser.add_option("-g", "--google-takeout-directory", dest="google_takeout_directory", help="Google Takeout Directory", metavar="DIRECTORY")
  parser.add_option("-m", "--access-token", dest="access_token", help="memair access token", metavar="TOKEN")
  (options, args) = parser.parse_args()

  if options.access_token == None:
    print("Please provide an access token. Create a temporary access token -> https://memair.com/generate_own_access_token")

  if options.google_takeout_directory == None:
    print("Please provide a Google takeout directory.")

  if (options.access_token == None) or (options.google_takeout_directory == None):
    print("See gtmem --help for options")
    exit()

  user = Memair(options.access_token)

  print(f'{datetime.datetime.now()} extracting google takeout location history...')
  getl = Getl(options.google_takeout_directory)
  getl.load_location_history()

  print(f'{datetime.datetime.now()} creating timestamp index on locations...')
  getl.sql('CREATE INDEX idx_locations_timestamp ON locations (timestamp);')

  total_locations_count = getl.sql("SELECT COUNT('cats') FROM locations")[0][0]
  print(f'{datetime.datetime.now()} {total_locations_count} locations extracted')

  last_import_at = (user.query(f'query{{Locations(order: desc order_by: timestamp first: 1 source: "{source}"){{timestamp}}}}')['data']['Locations'] or [{'timestamp': '1970-01-01 00:00:00'}])[0].get('timestamp')
  locations_count = getl.sql(f"SELECT COUNT('cats') FROM locations WHERE timestamp >= '{last_import_at}'")[0][0]
  print(f'{datetime.datetime.now()} {locations_count} since {last_import_at}')

  number_of_batches = ceil(locations_count / batch_size)

  for batch in list(range(number_of_batches)):
    print(f'{datetime.datetime.now()} extracting batch {batch + 1} of {number_of_batches}')
    locations = getl.sql(f'''
      SELECT
        latitude,
        longitude,
        accuracy,
        altitude,
        vertical_accuracy,
        timestamp
      FROM
        locations
      WHERE
        timestamp >= '{last_import_at}'
      ORDER BY timestamp, latitude, longitude
      LIMIT {batch * batch_size}, {batch_size}
    ''')
    location_query_string = ''
    for location in locations:
      location_query_string += f'{{ lat: {location[0]} lon: {location[1]} point_accuracy: {location[2] or "null"} altitude: {location[3] or "null"} altitude_accuracy: {location[4] or "null"} timestamp: "{location[5]}" source: "{source}" }}, '
    print(f'{datetime.datetime.now()} importing {len(locations)} locations into Memair')

    bulk_query_string = f'''
      mutation{{
        BulkCreate(
          locations: [
            {location_query_string}
          ]
        )
        {{
          id
          records_total
        }}
      }}
    '''
    query_kb = len(bulk_query_string.encode('utf-8')) / 1000

    print(f'{datetime.datetime.now()} uploading {query_kb} KBytes')
    results       = user.query(bulk_query_string)
    # if results contains errors
    batch_id      = results['data']['BulkCreate']['id']
    records_total = results['data']['BulkCreate']['records_total']
    print(f'{datetime.datetime.now()} Bulk Create "{batch_id}" created with {records_total} records accepted, waiting {sleep_time} seconds')
    sleep(sleep_time)

  print(f'{datetime.datetime.now()} finished!')
