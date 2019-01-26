import os
import decimal
import logging
import unittest
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
from unittest import mock

from yoyo import connections, read_migrations, get_backend

from .. import setUpModule  # noqa: F401 @UnusedImport
from ...storage import sqlite, StorageQueryError
from ...model import Record


class TestSqliteStorage(unittest.TestCase):

  all = {
    'level' : logging.DEBUG,
    'date'  : (None, None),
    'name'  : None,
    'query' : None
  }


  def setUp(self):
    dsn = 'sqlite:///:memory:'
    self.testee = sqlite.Storage(urlparse(dsn))

    migrations = read_migrations(
      os.path.join(os.path.dirname(__file__), '..', '..', 'migration', 'sqlite'))
    with mock.patch.object(connections.BACKENDS['sqlite'], 'connect') as m:
      m.return_value = self.testee._db

      backend = get_backend(dsn, migration_table = 'schema_version')
      backend.apply_migrations(backend.to_apply(migrations))

  def testRecord(self):
    self.assertEqual(0, self.testee.count(self.all))

    now = datetime.now(timezone.utc).replace(microsecond = 0)
    expected = Record(
      'some.test', now, logging.INFO, 'The Realm of Shades', {'foo': [{'bar': -1}]})
    actual = self.testee.record([expected])[0]
    self.assertEqual(expected.name, actual.name)
    self.assertEqual(expected.ts, actual.ts)
    self.assertEqual(expected.level, actual.level)
    self.assertEqual(expected.message, actual.message)
    self.assertEqual(expected.logrec, actual.logrec)

    self.assertEqual(1, self.testee.count(self.all))

    actualRangeItem = self.testee.range(0, 0, self.all)[0]
    self.assertGreater(actualRangeItem.id, 0)
    self.assertEqual('some.test', actualRangeItem.name)
    self.assertEqual(logging.INFO, actualRangeItem.level)
    self.assertEqual('The Realm of Shades', actualRangeItem.message)
    self.assertEqual(now, actualRangeItem.ts)

    actualItem = self.testee.get(actualRangeItem.id)
    self.assertEqual(actualRangeItem.id, actualItem.id)
    self.assertEqual('some.test', actualItem.name)
    self.assertEqual(logging.INFO, actualItem.level)
    self.assertEqual(now, actualItem.ts)
    self.assertEqual('The Realm of Shades', actualItem.message)
    self.assertEqual({'foo': [{'bar': -1}]}, actualItem.logrec)

  def testRecordMicroseconds(self):
    now = datetime.now(timezone.utc).replace(microsecond = 123456)
    expected = Record(
      'some.test', now, logging.INFO, 'The Realm of Shades', {'foo': [{'bar': -1}]})
    actual = self.testee.record([expected])[0]
    self.assertEqual(expected, actual)

    actual = self.testee.get(actual.id)
    self.assertEqual(expected, actual)

  def testRecordMultiple(self):
    now = datetime.now(timezone.utc).replace(microsecond = 0)
    records = self.testee.record([
      Record(
        'mutli.test{}'.format(i), now - timedelta(days = i), logging.WARN,
        'Hardcore Will Never Die, But You Will', {'track': 'Rano Pano'})
      for i in range(5)])

    for r in records:
      self.assertEqual(r, self.testee.get(r.id))

  def testGet(self):
    now = datetime.now(timezone.utc).replace(microsecond = 0)
    rec = {
      'int': 26,
      'float': 0.1,
      'decimal': decimal.Decimal('0.1'),
      'list': list(range(4)),
      'dict': dict(zip(range(4), range(3, -1, -1))),
      'none': None,
      'object': object()
    }
    id = self.testee.record([Record('some.test', now, logging.INFO, None, rec)])[0].id

    actual = self.testee.get(id).logrec
    self.assertEqual(26, actual['int'])
    self.assertEqual(0.1, actual['float'])
    self.assertEqual('0.1', actual['decimal'])
    self.assertEqual([0, 1, 2, 3], actual['list'])
    self.assertEqual({'0': 3, '1': 2, '2': 1, '3': 0}, actual['dict'])
    self.assertEqual(None, actual['none'])
    self.assertTrue(actual['object'].startswith('<object object at'))

  def testCount(self):
    self.assertEqual(0, self.testee.count(self.all))

    now = datetime.now(timezone.utc).replace(microsecond = 0)
    self.testee.record([
      Record(
        'some.test', now, logging.INFO, 'The Realm of Shades', {'key': [{'a': 1}, {'b': 2}]}),
      Record(
        'something.test', now, logging.WARN, 'The Realm of Shades', {'key': [{'a': 1}]})
    ])

    self.assertEqual(2, self.testee.count(self.all))

    self.assertEqual(0, self.testee.count(dict(self.all, level = logging.ERROR)))
    self.assertEqual(1, self.testee.count(dict(self.all, level = logging.WARN)))
    self.assertEqual(2, self.testee.count(dict(self.all, level = logging.INFO)))

    self.assertEqual(0, self.testee.count(dict(
      self.all, date = (now - timedelta(seconds = 10), now - timedelta(seconds = 5)))))
    self.assertEqual(0, self.testee.count(dict(
      self.all, level = logging.INFO,
      date = (now - timedelta(seconds = 10), now - timedelta(seconds = 5)))))
    self.assertEqual(2, self.testee.count(dict(
      self.all, level = logging.INFO,
      date = (now - timedelta(seconds = 10), now + timedelta(seconds = 5)))))

    self.assertEqual(0, self.testee.count(dict(self.all, name = 'foo')))
    self.assertEqual(1, self.testee.count(dict(self.all, name = 'some.')))
    self.assertEqual(1, self.testee.count(dict(self.all, name = 'something')))
    self.assertEqual(2, self.testee.count(dict(self.all, name = 'some, something')))
    self.assertEqual(2, self.testee.count(dict(self.all, name = 'so')))

    self.assertEqual(
      2, self.testee.count(dict(self.all, query = "json_extract(logrec, '$.key[0].a') = 1")))
    self.assertEqual(
      1, self.testee.count(dict(self.all, query = "json_extract(logrec, '$.key[1].b') = 2")))

    self.assertEqual(1, self.testee.count(dict(
      self.all,
      query = "json_extract(logrec, '$.key[1].b') = 2",
      level = logging.INFO,
      date = (now - timedelta(seconds = 10), now + timedelta(seconds = 5))
    )))

  def testCountBadQuery(self):
    with self.assertRaises(StorageQueryError):
      self.testee.count(dict(self.all, query = 'logrec->$#!'))

  def testCountHistogram(self):
    now = datetime(2017, 6, 17, 23, 14, 37, tzinfo = timezone.utc)

    self.testee.record([Record(
      'something.test', now + timedelta(minutes = i * 5, microseconds = i * 50),
      logging.WARN, 'Fela the Congueror', {'a': 1}) for i in range(16)])

    actual = self.testee.count(self.all, group = True)
    self.assertEqual((
      (datetime(2017, 6, 17, 23, 0,  tzinfo = timezone.utc), 1),
      (datetime(2017, 6, 17, 23, 15, tzinfo = timezone.utc), 3),
      (datetime(2017, 6, 17, 23, 30, tzinfo = timezone.utc), 3),
      (datetime(2017, 6, 17, 23, 45, tzinfo = timezone.utc), 3),
      (datetime(2017, 6, 18, 0,  0,  tzinfo = timezone.utc), 3),
      (datetime(2017, 6, 18, 0,  15, tzinfo = timezone.utc), 3),
    ), actual)

    actual = self.testee.count(
      dict(
        self.all, date=(now + timedelta(minutes = 59), None),
        query = "json_extract(logrec, '$.a') = 1"),
      group = True)
    self.assertEqual((
      (datetime(2017, 6, 18, 0, 0,  tzinfo = timezone.utc), 1),
      (datetime(2017, 6, 18, 0, 15, tzinfo = timezone.utc), 3),
    ), actual)

  def testRange(self):
    now = datetime.now(timezone.utc).replace(microsecond = 0)
    self.testee.record([
      Record(
        'some.test', now, logging.INFO, 'The Realm of Shades', {'key': [{'a': 1}, {'b': 2}]}),
      Record(
        'something.test', now, logging.WARN, 'The Realm of Shades', {'key': [{'a': 1}]})
    ])

    actual = tuple(r.asdict() for r in self.testee.range(0, 1, self.all))
    self.assertEqual(2, len(actual))
    self.assertGreater(actual[0]['id'], actual[1]['id'])
    [r.pop('id') for r in actual]
    self.assertEqual((
      {
        'level': 30, 'name': 'something.test', 'ts': now,
        'message': 'The Realm of Shades', 'logrec': {'key': [{'a': 1}]}},
      {
        'level': 20, 'name': 'some.test', 'ts': now,
        'message': 'The Realm of Shades', 'logrec': {'key': [{'a': 1}, {'b': 2}]}}
    ), actual)

    actual = self.testee.range(0, 0, self.all)
    self.assertEqual(1, len(actual))
    self.assertEqual('something.test', actual[0].name)

    actual = self.testee.range(1, 1, self.all)
    self.assertEqual(1, len(actual))
    self.assertEqual('some.test', actual[0].name)

    actual = self.testee.range(1, 0, self.all)
    self.assertEqual([], actual)

    actual = self.testee.range(
      0, 0, dict(
        self.all,
        query = "json_extract(logrec, '$.key[1].b') = 2",
        level = logging.INFO,
        date = (now - timedelta(seconds = 10), now + timedelta(seconds = 5))
      )
    )
    self.assertEqual(1, len(actual))
    self.assertEqual('some.test', actual[0].name)

  def testRangeBadQuery(self):
    with self.assertRaises(StorageQueryError):
      self.testee.range(0, 0, dict(self.all, query = "json(logrec, '$.key[1].b')"))

  def testPurge(self):
    now = datetime.now(timezone.utc).replace(microsecond = 0)
    now -= timedelta(seconds = 10)  # Avoid race condition on middle record
    records = self.testee.record([
      Record(
        'purge.test', now - timedelta(days = i), logging.INFO,
        'Hardcore Will Never Die, But You Will', {'track': 'Death Rays'})
      for i in range(11)])
    record_ids = [r.id for r in records]

    cur = self.testee._db.cursor()
    cur.execute('SELECT record_id FROM record')

    purged = self.testee.purge(timedelta(days = 5))
    self.assertEqual(6, purged)
    self.assertEqual(5, self.testee.count(self.all))

    recordsLeft = self.testee.range(0, 10, self.all)
    self.assertEqual(record_ids[:5], [r.id for r in reversed(recordsLeft)])

  def testPurgeOlderFraction(self):
    now = datetime.now(timezone.utc).replace(microsecond = 0)
    now -= timedelta(seconds = 10)  # Avoid race condition on middle record
    records = self.testee.record([
      Record(
        'purge.test', now - timedelta(days = i), logging.INFO,
        'Hardcore Will Never Die, But You Will', {'track': 'Death Rays'})
      for i in range(11)])
    record_ids = [r.id for r in records]

    cur = self.testee._db.cursor()
    cur.execute('SELECT record_id FROM record')

    purged = self.testee.purge(timedelta(days = 5.1))
    self.assertEqual(5, purged)
    self.assertEqual(6, self.testee.count(self.all))

    recordsLeft = self.testee.range(0, 10, self.all)
    self.assertEqual(record_ids[:6], [r.id for r in reversed(recordsLeft)])

