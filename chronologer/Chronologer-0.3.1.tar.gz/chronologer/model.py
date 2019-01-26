import ast
import time
import logging
import itertools
from datetime import datetime, timezone
from collections import OrderedDict

import pytz


__all__ = 'Record', 'createRecord', 'groupTimeseries'


RefRec = logging.makeLogRecord({})
RefRec.origname = None


class Record:

  __slots__ = 'name', 'ts', 'level', 'message', 'logrec', 'id'


  def __init__(self, name, ts, level, message, logrec = None, id = None):
    self.name = name
    self.ts = ts
    self.level = level
    self.message = message
    self.logrec = logrec
    self.id = id

  def __repr__(self):
    return 'Record({})'.format(', '.join('{}={!r}'.format(k, v) for k, v in self.asdict().items()))

  def __eq__(self, other):
    return self.asdict() == other.asdict()

  def asdict(self):
    return OrderedDict(((name, getattr(self, name)) for name in self.__slots__))


class ModelError(Exception):
  '''Generic model error'''


def createRecord(logdict, *, raw = False, parse = False):
  if parse:
    logdict = restoreTypes(logdict)

  if raw:
    return createRawRecord(logdict)
  else:
    return createLoggingRecord(logdict)

def createLoggingRecord(logdict):
  '''Create a logging record.
  See https://docs.python.org/3/library/logging.html#logrecord-attributes'''

  try:
    name  = logdict.pop('name')
    ts    = datetime.utcfromtimestamp(logdict.pop('created')).replace(tzinfo = timezone.utc)
    level = logdict.pop('levelno')

    # There's no message but only 'msg' when no string interpolation takes place
    message = logdict.pop('message') if 'message' in logdict else logdict['msg']

    # Remove redundant attributes. 'asctime' is not always present.
    for k in ('levelname', 'asctime'):
      logdict.pop(k, None)

    error = {}
    if not logdict['exc_text']:
      del logdict['exc_info'], logdict['exc_text']
    else:
      error.update(exc_info = logdict.pop('exc_info'), exc_text = logdict.pop('exc_text'))
  except KeyError as ex:
    raise ModelError('Key "{}" is missing'.format(ex.args[0]))

  meta = {}
  data = {}
  for k, v in logdict.items():
    if hasattr(RefRec, k):
      meta[k] = v
    else:
      data[k] = v

  scope  = locals()
  logrec = {n: scope[n] for n in ('data', 'meta', 'error') if scope[n]}

  return Record(name, ts, level, message, logrec)

def createRawRecord(logdict):
  '''Create record without processing meta fields and keeping whole
  ``logdict`` in ``logrec`` fields.'''

  name    = logdict.get('name', '')
  message = logdict.get('message', '')
  level   = logdict.get('levelno', logging.INFO)
  ts      = datetime.utcfromtimestamp(
    logdict.get('created', time.time())).replace(tzinfo = timezone.utc)

  return Record(name, ts, level, message, logdict)

def restoreTypes(logdict):
  '''Try evaluate values of the dictionary to get original types
  and nested structures that were before URL encoding.'''

  for k, v in logdict.items():
    try:
      logdict[k] = ast.literal_eval(v)
    except (SyntaxError, ValueError):
      pass

  return logdict


intervals = {
  'day'  : {'hour': 0, 'minute': 0, 'second': 0, 'tzinfo': None},
  'hour' : {'minute': 0, 'second': 0, 'tzinfo': None}
}

def groupTimeseries(seq, interval, tz):
  '''Group tuple(dt, count) sequence in coarser time interval'''

  sub = intervals[interval]
  tz  = pytz.timezone(tz)
  for k, g in itertools.groupby(seq, key = lambda v: v[0].astimezone(tz).replace(**sub)):
    # The tzinfo is reset and re-localised to avoid duplicate time keys during DST
    yield tz.localize(k), sum(v[1] for v in g)

