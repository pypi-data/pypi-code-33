import os
from empatican.physio import e4
# from django.test import TestCase
from dateutil import parser
from datetime import datetime
import pandas as pd
import pytz
import tempfile
from unittest import TestCase, skipIf

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'fixtures')


class E4StreamTest(TestCase):
    # def setUp(self):
    #     print(self._testMethodName)

    def test_e4_stream_unzipped_csv(self):
        acc_csv = os.path.join(FIXTURES_DIR, 'e4', 'ACC.csv')
        example = dict(
            timestamp=1533751118,
            freq=32,
            n_samples=2000,
            last_datetime=parser.parse('2018-08-08 17:59:40.468750+0:00'))

        acc_stream = e4.AccStream(acc_csv)
        last_datetime = acc_stream.data.index[-1].to_pydatetime()

        self.assertEqual(acc_stream.start_timestamp, example['timestamp'])
        self.assertEqual(acc_stream.frequency, example['freq'])
        self.assertEqual(acc_stream.data.shape[0], example['n_samples'])
        self.assertEqual(list(acc_stream.data.columns), ['x', 'y', 'z'])
        self.assertEqual(last_datetime, example['last_datetime'])

    def test_e4_stream_zipped_csv(self):
        acc_csv = os.path.join(FIXTURES_DIR, 'e4', 'ACC.csv.gz')
        timestamp = 1533751118
        example = dict(
            timestamp=timestamp,
            freq=32,
            n_samples=2000,
            first_datetime=datetime.fromtimestamp(timestamp, tz=pytz.utc),
            last_datetime=parser.parse('2018-08-08 17:59:40.468750+0:00'))

        acc_stream = e4.AccStream(acc_csv)
        first_datetime = acc_stream.data.index[0].to_pydatetime()
        last_datetime = acc_stream.data.index[-1].to_pydatetime()

        self.assertEqual(acc_stream.start_timestamp, example['timestamp'])
        self.assertEqual(acc_stream.frequency, example['freq'])
        self.assertEqual(acc_stream.data.shape[0], example['n_samples'])
        self.assertEqual(list(acc_stream.data.columns), ['x', 'y', 'z'])
        self.assertEqual(first_datetime, example['first_datetime'])
        self.assertEqual(last_datetime, example['last_datetime'])

    def test_e4_bvp_csv(self):
        bvp_csv = os.path.join(FIXTURES_DIR, 'e4', 'BVP.csv')
        example_timestamp, example_freq, example_n_samples = (1533751118, 64,
                                                              2000)

        bvp_stream = e4.BvpStream(bvp_csv)
        self.assertEqual(bvp_stream.start_timestamp, example_timestamp)
        self.assertEqual(bvp_stream.frequency, example_freq)
        self.assertEqual(bvp_stream.data.shape[0], example_n_samples)
        self.assertEqual(bvp_stream.data.columns, ['bvp'])

    def test_e4_eda_csv(self):
        eda_csv = os.path.join(FIXTURES_DIR, 'e4', ('EDA.csv'))
        example_timestamp, example_freq, example_n_samples = (1533751118, 4,
                                                              200)

        eda_stream = e4.EdaStream(eda_csv)
        self.assertEqual(eda_stream.start_timestamp, example_timestamp)
        self.assertEqual(eda_stream.frequency, example_freq)
        self.assertEqual(eda_stream.data.shape[0], example_n_samples)
        self.assertEqual(eda_stream.data.columns, ['eda'])

    def test_e4_hr_csv(self):
        hr_csv = os.path.join(FIXTURES_DIR, 'e4', ('HR.csv'))
        example_timestamp, example_freq, example_n_samples = (1533751128, 1,
                                                              1579)

        hr_stream = e4.HrStream(hr_csv)
        self.assertEqual(hr_stream.start_timestamp, example_timestamp)
        self.assertEqual(hr_stream.frequency, example_freq)
        self.assertEqual(hr_stream.data.shape[0], example_n_samples)
        self.assertEqual(hr_stream.data.columns, ['hr'])

    def test_e4_ibi_csv(self):
        ibi_csv = os.path.join(FIXTURES_DIR, 'e4', ('IBI.csv'))

        timestamp = 1533751118
        first_example = datetime.fromtimestamp(
            timestamp, tz=pytz.utc).replace(microsecond=0)

        example = dict(
            timestamp=timestamp,
            freq=None,
            n_samples=121,
            first_datetime=first_example,
            last_datetime=parser.parse('2018-08-08T18:15:47.765887+0:00'))

        ibi_stream = e4.IbiStream(ibi_csv)

        first_datetime = ibi_stream.data.index[0].replace(
            microsecond=0, nanosecond=0).to_pydatetime()
        last_datetime = ibi_stream.data.index[-1].replace(
            nanosecond=0).to_pydatetime()

        self.assertEqual(ibi_stream.start_timestamp, example['timestamp'])
        self.assertEqual(ibi_stream.frequency, example['freq'])
        self.assertEqual(ibi_stream.data.shape[0], example['n_samples'])
        self.assertEqual(ibi_stream.data.columns, ['ibi'])

        # TODO nb Testing of the first timestamp for a time-delta index is
        # really the initial timestamp plus the first offset
        self.assertEqual(first_datetime, example['first_datetime'])
        self.assertEqual(last_datetime,
                         example['last_datetime'].astimezone(pytz.utc))

    def test_e4_press_csv(self):
        csv = os.path.join(FIXTURES_DIR, 'e4', ('tags.csv'))

        timestamp = None
        example = dict(
            timestamp=timestamp,
            freq=None,
            n_samples=3,
            first_datetime=datetime.fromtimestamp(1533751266.23, tz=pytz.utc),
            last_datetime=datetime.fromtimestamp(1533752705.76, tz=pytz.utc))

        stream = e4.PressStream(csv)

        first_datetime = stream.data.index[0].replace(
            nanosecond=0).to_pydatetime()
        last_datetime = stream.data.index[-1].replace(
            nanosecond=0).to_pydatetime()

        self.assertEqual(stream.start_timestamp, example['timestamp'])
        self.assertEqual(stream.frequency, example['freq'])
        self.assertEqual(stream.data.shape[0], example['n_samples'])
        self.assertEqual(stream.data.columns, ['press'])
        self.assertEqual(first_datetime, example['first_datetime'])

        # Rounding error in nanoseconds with the last datetime

        self.assertEqual(last_datetime.year, example['last_datetime'].year)
        self.assertEqual(last_datetime.month, example['last_datetime'].month)
        self.assertEqual(last_datetime.day, example['last_datetime'].day)
        self.assertEqual(last_datetime.hour, example['last_datetime'].hour)
        self.assertEqual(last_datetime.minute, example['last_datetime'].minute)
        self.assertEqual(last_datetime.second, example['last_datetime'].second)

    def test_e4_temperature_csv(self):
        temperature_csv = os.path.join(FIXTURES_DIR, 'e4', ('TEMP.csv'))
        example_timestamp, example_freq, example_n_samples = (1533751118, 4,
                                                              6352)

        temperature_stream = e4.TemperatureStream(temperature_csv)
        self.assertEqual(temperature_stream.start_timestamp, example_timestamp)
        self.assertEqual(temperature_stream.frequency, example_freq)
        self.assertEqual(temperature_stream.data.shape[0], example_n_samples)
        self.assertEqual(temperature_stream.data.columns, ['temperature'])


class E4SessionTest(TestCase):
    def test_e4_session_dir(self):
        session_path = os.path.join(FIXTURES_DIR, 'e4')
        example = dict(timestamp=1533751118, hr_timestamp=1533751128)

        session = e4.Session(session_path)

        # Just check stream timestamps (more detailed testing of streams above)
        self.assertEqual(session.streams['acc'].start_timestamp,
                         example['timestamp'])
        self.assertEqual(session.streams['bvp'].start_timestamp,
                         example['timestamp'])
        self.assertEqual(session.streams['eda'].start_timestamp,
                         example['timestamp'])
        self.assertEqual(session.streams['hr'].start_timestamp,
                         example['hr_timestamp'])
        self.assertEqual(session.streams['ibi'].start_timestamp,
                         example['timestamp'])
        self.assertEqual(session.streams['temperature'].start_timestamp,
                         example['timestamp'])
        # nb Press / tags stream is odd and has no timestamp
        self.assertEqual(session.streams['press'].start_timestamp, None)
        self.assertEqual(session.streams['press'].num_samples, 3)

        # Check that session metadata was loaded appropriately
        self.assertEqual(session.e4_meta['device_id'], '54a32b')
        self.assertEqual(session.e4_meta['start_time'], 1533751118)
        self.assertEqual(session.e4_meta['duration'], 62.46875)
        self.assertEqual(session.e4_meta['label'], '5693')
        self.assertEqual(session.e4_meta['device'], 'E4 2.1')

        # Cleanup
        del (session)

    def test_e4_session_dir_nometa(self):
        session_path = os.path.join(FIXTURES_DIR, 'e4_nometa')
        example = dict(timestamp=1533751118, hr_timestamp=1533751128)

        session = e4.Session(session_path)

        # Just check stream timestamps (more detailed testing of streams above)
        self.assertEqual(session.streams['acc'].start_timestamp,
                         example['timestamp'])
        self.assertEqual(session.streams['bvp'].start_timestamp,
                         example['timestamp'])
        self.assertEqual(session.streams['eda'].start_timestamp,
                         example['timestamp'])
        self.assertEqual(session.streams['hr'].start_timestamp,
                         example['hr_timestamp'])
        self.assertEqual(session.streams['ibi'].start_timestamp,
                         example['timestamp'])
        self.assertEqual(session.streams['temperature'].start_timestamp,
                         example['timestamp'])
        # nb Press / tags stream is odd and has no timestamp
        self.assertEqual(session.streams['press'].start_timestamp, None)
        self.assertEqual(session.streams['press'].num_samples, 3)

        # E4 Meta should be empty
        self.assertEqual(session.e4_meta, {})

        # Cleanup
        del (session)

    def test_e4_session_zip(self):
        session_path = os.path.join(FIXTURES_DIR, 'zips', 'Sess01.zip')
        example = dict(timestamp=1533751118, hr_timestamp=1533751128)

        session = e4.Session(session_path)

        # Just check stream timestamps (more detailed testing of streams above)
        self.assertEqual(session.streams['acc'].start_timestamp,
                         example['timestamp'])
        self.assertEqual(session.streams['bvp'].start_timestamp,
                         example['timestamp'])
        self.assertEqual(session.streams['eda'].start_timestamp,
                         example['timestamp'])
        self.assertEqual(session.streams['hr'].start_timestamp,
                         example['hr_timestamp'])
        self.assertEqual(session.streams['ibi'].start_timestamp,
                         example['timestamp'])
        self.assertEqual(session.streams['temperature'].start_timestamp,
                         example['timestamp'])
        # nb Press / tags stream is odd and has no timestamp
        self.assertEqual(session.streams['press'].start_timestamp, None)
        self.assertEqual(session.streams['press'].num_samples, 3)

        del (session.source_path)

    def test_e4_session_ioerror(self):
        bad_path = os.path.join(FIXTURES_DIR, 'zips', 'Badpath.zip')

        with self.assertRaises(IOError):
            e4.Session(bad_path)

    @skipIf(not e4.hdf_available, "Missing HDF Support")
    def test_e4_session_to_hdf(self):
        session_path = os.path.join(FIXTURES_DIR, 'e4')
        session = e4.Session(session_path)
        h5_fname = 'session.h5'

        with tempfile.NamedTemporaryFile() as h5_tmp:
            h5_fname = h5_tmp.name
            session.to_hdf(h5_fname)

            self.assertTrue(os.path.getsize(h5_fname) > 0)

            # Read the new h5 file and make sure it was stored correctly
            with pd.HDFStore(h5_fname) as store:
                acc_attrs = store.get_storer('dt/acc').attrs
                self.assertEqual(session.streams['acc'].start_timestamp,
                                 acc_attrs.metadata['start_timestamp'])

    @skipIf(not e4.hdf_available, "Missing HDF Support")
    def test_e4_session_from_hdf(self):
        session_path = os.path.join(FIXTURES_DIR, 'e4')
        example_session = e4.Session(session_path)

        h5_fname = os.path.join(FIXTURES_DIR, 'zips/Sess01.h5')

        session = e4.Session(h5_fname)

        self.assertEqual(session.streams['acc'].start_timestamp,
                         example_session.streams['acc'].start_timestamp)
        self.assertEqual(session.streams['acc'].frequency,
                         example_session.streams['acc'].frequency)
        self.assertEqual(session.streams['acc'].num_samples,
                         example_session.streams['acc'].num_samples)
        self.assertEqual(
            os.path.basename(session.streams['acc'].filepath),
            os.path.basename(example_session.streams['acc'].filepath))

    def test_e4_stream_to_csv(self):
        acc_csv = os.path.join(FIXTURES_DIR, 'e4', 'ACC.csv')
        acc_stream = e4.AccStream(acc_csv)

        with tempfile.NamedTemporaryFile() as acc_tmp:
            # out_csv = 'ACC.csv'  # for quick checking
            out_csv = acc_tmp.name
            acc_stream.to_csv(out_csv)
            self.assertTrue(os.path.getsize(out_csv) > 0)

    def test_e4_session_to_csv(self):
        session_path = os.path.join(FIXTURES_DIR, 'e4')
        session = e4.Session(session_path)

        # Output as a full directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = os.path.join(tmp_dir, 'Session')
            # tmp_path = './Session'  # Local testing
            session.to_archive(tmp_path)
            self.assertTrue(os.path.exists(os.path.join(tmp_path, 'ACC.csv')))

        # Output as a zip archive
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = os.path.join(tmp_dir, 'Session.zip')
            # tmp_path = './Session.zip'  # Local testing
            session.to_archive(tmp_path)
            self.assertTrue(os.path.getsize(tmp_path) > 0)

        # Test IOError
        with tempfile.TemporaryDirectory() as tmp_dir:
            existing_dir = os.path.join(tmp_dir, 'ImHereAlready')
            os.makedirs(existing_dir)
            with self.assertRaises(IOError):
                session.to_archive(existing_dir)
