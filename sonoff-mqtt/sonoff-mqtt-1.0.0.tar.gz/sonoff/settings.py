import os
import json
from pathlib import Path

# Load our settings from the config file (generated using sonoff-mqtt-config).
path = Path(__file__).parent / '.wifi.json'
wifi = json.load(path.open())

SERVER_ADDRESS = wifi['serverName']
SERVER_PORT = wifi['port']

API_KEY = '111111111-1111-1111-1111-111111111111'

# Allow overriding with environment variables.
for key, value in list(locals().items()):
    if key.upper() == key and key in os.environ:
        locals()[key] = os.environ[key]
