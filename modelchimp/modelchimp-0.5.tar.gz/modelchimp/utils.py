import hashlib
import time
import pytz
import re

from uuid import uuid4
from base64 import b64encode
from datetime import datetime


def generate_uid():
  t = b64encode(str(time.time()).encode('utf-8'))
  r = b64encode(str(uuid4()).encode('utf-8'))
  return hashlib.sha256(t + r).hexdigest()


def current_string_datetime():
    dt = datetime.now(pytz.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")


def is_uuid4_pattern(text):
    pattern =  re.compile(
        (
            '[a-f0-9]{8}-' +
            '[a-f0-9]{4}-' +
            '4' + '[a-f0-9]{3}-' +
            '[89ab][a-f0-9]{3}-' +
            '[a-f0-9]{12}$'
        ),
        re.IGNORECASE
    )
    return pattern.match(text)
