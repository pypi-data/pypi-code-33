__version__ = '0.3.0'

from influxdb import InfluxDBClient
import geohash2
import logging
from geolite2 import geolite2
import click
import re
from typing import List, Dict, Union
from hashlib import sha256
from base64 import b64encode

Event = Dict[str,Union[str, Dict]]

def parse_ringserver_log(filename: str) -> List[Event]:
    """
    Read a txlog file and parses information.
    Returns a list of events (dictionary)
    """
    logstart_pattern = r'START CLIENT (?P<hostname>\b(?:[0-9A-Za-z][0-9A-Za-z-]{0,62})(?:\.(?:[0-9A-Za-z][0-9A-Za-z-]{0,62}))*(\.?|\b)) \[(?P<ip>(?<![0-9])(?:(?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5]))(?![0-9]))\] \((?P<agent>.*)\) @ .*\(connected (?P<timestamp>[0-9]+-[0-9]+-[0-9]+ (?:2[0123]|[01]?[0-9]):(?:[0-5][0-9]):(?:[0-5][0-9]))\) TX'
    logevent_pattern = '(?P<network>[A-Z0-9]*)_(?P<station>[A-Z0-9]*)_(?P<location>[A-Z0-9]*)_(?P<channel>[A-Z0-9]*)/MSEED (?P<bytes>[0-9]+) (?P<packets>[0-9]+)'
    georeader = geolite2.reader()
    process_events = True

    events = []
    with open(filename, 'r') as file:
        for log in file:
            # log line exemple: START CLIENT 52.red-88-2-197.staticip.rima-tde.net [88.2.197.52] (SeedLink|SeedLink Client) @ 2016-11-28 00:00:00 (connected 2016-11-26 16:37:07) TX
            if log.startswith('START CLIENT'):
                events_data = re.search(logstart_pattern, log)
                if events_data == None:
                    logging.error("Unable to parse START log line: %s"%(log))
                    process_events = False
                    continue
                events_data = events_data.groupdict()
                location = georeader.get(events_data['ip'])
                events_data['geohash'] = geohash2.encode(location['location']['latitude'], location['location']['longitude'])
                events_data['hostname'] = b64encode(sha256(events_data['hostname'].encode()).digest())[:12] # complicated oneliner to hash the hostname
                logging.debug(events_data)
            elif log.startswith('END CLIENT'):
                process_events = True
            elif process_events:
                # line exemple :
                # FR_SURF_00_HHZ/MSEED 21511168 42014
                event = re.search(logevent_pattern, log)
                if event == None:
                    logging.error("Unable to parse log : %s"%(log))
                    continue
                event = event.groupdict()
                logging.debug(event)
                events.append({**events_data, **event})
    return(events)

def influxdb_send_data(dbhost: str, dbport: int, dbname: str, verifyssl: bool, dbuser: str, password: str, data: List[Dict]) -> bool:
    """
    Sends data into influxdb
    """
    try:
        logging.info("Sending data to influxdb")
        logging.debug("host     = "+dbhost)
        logging.debug("database = "+dbname)
        logging.debug("username = "+dbuser)

        client = InfluxDBClient(host     = dbhost,
                                port     = dbport,
                                database = dbname,
                                username = dbuser,
                                password = password,
                                ssl      = True,
                                verify_ssl = verifyssl
        )

        client.write_points(data)
    except Exception as e:
        logging.error("Unexpected error writing data to influxdb")
        logging.error(e)
        return False
    return True

@click.command()
@click.option('--influxdbhost',  'dbhost',  help='Influxdb hostname or adress.', envvar='INFLUXDB_HOST')
@click.option('--influxdbport',  'dbport', help='Influxdb port. Default: 8086', envvar='INFLUXDB_PORT', default=8086, type=click.INT)
@click.option('--influxdbdb',    'dbname',   help='Influxdb database.', envvar='INFLUXDB_DB')
@click.option('--verifyssl/--no-verifyssl', help='Should the connexion do SSL check ?', default=False, envvar='INFLUXDB_VERIFY_SSL')
@click.option('--influxdbuser',  'dbuser', help='Influxdb user', envvar='INFLUXDB_USER')
@click.option('--influxdbpass',  'password', help='Influxdb pass', envvar='INFLUXDB_PASS')
@click.argument('files', type=click.Path(exists=True), nargs=-1)
def cli(dbhost: str, dbport: int, dbname: str, verifyssl: bool, dbuser: str, password: str, files: List):
    influxdb_json_data = []
    for f in files:
        logging.debug("Opening file %s"%(f))
        # Parsing events from a logfile
        for event in  parse_ringserver_log(f):
            # Constructing an influxdb data from the event
            influxdb_json_data.append(
                {"measurement": 'ringserverstats',
                 "tags": {
                     "network": event['network'],
                     "station": event['station'],
                     "location": event['location'],
                     "channel": event['channel'],
                     "geohash": event['geohash'],
                     "agent":   event['agent'],
                     "hosthash": event['hostname']
                 },
                 "time": event['timestamp'].replace(' ','T')+'Z',
                 "fields": {
                         "bytes": int(event['bytes'])
                 }
                }
            )
    influxdb_send_data(dbhost, dbport, dbname, verifyssl, dbuser, password, influxdb_json_data)
