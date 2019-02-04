import json
from pathlib import Path

path = Path(__file__).parent / '.wifi.json'
backup = Path(__file__).parent / '.wifi.json~'

if path.exists():
    wifi = json.load(path.open())
else:
    wifi = {
        'serverName': '',
        'port': '',
        'version': 4,
        'ssid': '',
        'password': ''
    }

keys = [
    'ssid',
    'password',
    'serverName',
    'port',
]


def main():
    for key in keys:
        wifi[key] = input(f'Enter {key} [{wifi[key]}]: ') or wifi.get(key)
    if path.exists():
        backup.write_text(path.read_text())
    json.dump(wifi, fp=path.open('w'), indent=2)
