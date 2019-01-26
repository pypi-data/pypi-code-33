import os
from urllib import request, parse

from .utils import get_logger
log = get_logger(__name__)

GA_PROPERTY_ID = 'UA-129796740-3'
# REQUEST_URL = 'https://www.google-analytics.com/debug/collect'
REQUEST_URL = 'https://www.google-analytics.com/collect'


# Todo: convert this to an updates check.
def send_anonymous_usage(auid, usage_type='NoneSet'):
  try:
    payload = parse.urlencode({
      'v': '1',
      'tid': GA_PROPERTY_ID,
      'aip': '1',
      'cid': auid,
      'cd1': auid,
      't': 'event',
      'ec': 'run_transforms',
      'ea': usage_type,
    }).encode()

    req =  request.Request(REQUEST_URL, data=payload)
    resp = request.urlopen(req)

    # log.debug(f'Anonymous usage sent with status {resp.status}')
  except Exception as e:
    # log.debug(f'Anonymous usage failed to send with exception {e}')
    resp = False

  return(resp)