import sys
import requests
import signal


def signal_handler(signum, frame):
    pass


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGABRT, signal_handler)


def _put_file(signed_url, data):
    post_res = requests.put(signed_url, data=data)
    post_res.raise_for_status()


filepath = sys.argv[1]
signed_url = sys.argv[2]
with open(filepath, 'rb') as data:
    _put_file(signed_url, data)
