import unittest
import csv
from pirev.pirev import getInfo
from pirev.revinfo import getRevInfo

def testDataPath(filename):
  return f'test/data/{filename}'

def readTsvData(filename):
  with open(filename) as tsvfile:
    reader = csv.DictReader(tsvfile, dialect='excel-tab')
    return list(dict((k.lower(), v) for k,v in row.items()) for row in reader)

CPUINFO_PI1 = testDataPath('cpuinfo_pi1')
CPUINFO_PI3 = testDataPath('cpuinfo_pi3')
CPUINFO_MBP = testDataPath('cpuinfo_mbp')
MISSING_FILE = testDataPath('missing')
OLD_CODES = testDataPath('codes_old.tsv')
NEW_CODES = testDataPath('codes_new.tsv')

class TestGetInfo(unittest.TestCase):

  def test_cpuinfo_pi1(self):
    info = getInfo(CPUINFO_PI1)

    self.assertEqual(info['revision'], {
      'type': 'B',
      'memory': '512 MB',
      'processor': 'BCM2835',
      'revision': 2.0,
      'manufacturer': 'Sony UK',
      'code': '000e',
    })

  def test_cpuinfo_pi3(self):
    info = getInfo(CPUINFO_PI3)

    self.assertEqual(info['revision'], {
      'type': '3B',
      'memory': '1 GB',
      'processor': 'BCM2837',
      'revision': 1.2,
      'manufacturer': 'Embest',
      'code': 'a22082',
    })

  def test_cpuinfo_mbp(self):
    with self.assertRaises(ReferenceError):
      getInfo(CPUINFO_MBP)

  def test_missing_file(self):
    with self.assertRaises(FileNotFoundError):
      getInfo(MISSING_FILE)

class TestRevInfo(unittest.TestCase):

  def test_parse_old_codes(self):
    data = readTsvData(OLD_CODES)

    for entry in data:
      info = getRevInfo(entry['code'])

      self.assertEqual(info['type'], entry['model'])
      self.assertEqual(info['memory'], entry['ram'])
      self.assertEqual(info['revision'], float(entry['revision']))
      self.assertEqual(info['manufacturer'], entry['manufacturer'])

  def test_parse_new_codes(self):
    data = readTsvData(NEW_CODES)

    for entry in data:
      info = getRevInfo(entry['code'])

      self.assertEqual(info['type'], entry['model'])
      self.assertEqual(info['memory'], entry['ram'])
      self.assertEqual(info['revision'], float(entry['revision']))
      self.assertEqual(info['manufacturer'], entry['manufacturer'])

if __name__ == '__main__':
    unittest.main()
