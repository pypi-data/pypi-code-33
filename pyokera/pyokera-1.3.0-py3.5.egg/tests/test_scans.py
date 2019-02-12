# Copyright 2017 Okera Inc. All Rights Reserved.
#
# Tests that should run on any configuration. The server auth can be specified
# as an environment variables before running this test.
# pylint: disable=bad-continuation,bad-indentation,global-statement,unused-argument
import unittest
import numpy

from okera.tests import pycerebro_test_common as common

retry_count = 0

class BasicTest(unittest.TestCase):
    def test_sparse_data(self):
        with common.get_planner() as planner:
            df = planner.scan_as_pandas("rs.sparsedata")
            self.assertEqual(96, len(df), msg=df)
            self.assertEqual(68, df['age'].count(), msg=df)
            self.assertEqual(10.0, df['age'].min(), msg=df)
            self.assertEqual(96.0, df['age'].max(), msg=df)
            self.assertEqual(b'sjc', df['defaultcity'].max(), msg=df)
            self.assertEqual(86, df['description'].count(), msg=df)

    def test_nulls(self):
        with common.get_planner() as planner:
            df = planner.scan_as_pandas("select string_col from rs.alltypes_null")
            self.assertEqual(1, len(df), msg=df)
            self.assertTrue(numpy.isnan(df['string_col'][0]), msg=df)

            df = planner.scan_as_pandas(
                "select length(string_col) as c from rs.alltypes_null")
            self.assertEqual(1, len(df), msg=df)
            self.assertTrue(numpy.isnan(df['c'][0]), msg=df)

    def test_timestamp_functions(self):
        with common.get_planner() as planner:
            json = planner.scan_as_json("""
                select date_add('2009-01-01', 10) as c from okera_sample.sample""")
            self.assertTrue(len(json) == 2, msg=json)
            self.assertEqual('2009-01-11 00:00:00+00:00', str(json[0]['c']), msg=json)
            self.assertEqual('2009-01-11 00:00:00+00:00', str(json[1]['c']), msg=json)

    def test_duplicate_cols(self):
        with common.get_planner() as planner:
            json = planner.scan_as_json("""
                select record, record from okera_sample.sample""")
            self.assertTrue(len(json) == 2, msg=json)
            self.assertEqual('This is a sample test file.', str(json[0]['record']),
                             msg=json)
            self.assertEqual('This is a sample test file.', str(json[0]['record_2']),
                             msg=json)

        with common.get_planner() as planner:
            json = planner.scan_as_json("""
                select record, record as record_2, record from okera_sample.sample""")
            self.assertTrue(len(json) == 2, msg=json)
            self.assertEqual('This is a sample test file.', str(json[0]['record']),
                             msg=json)
            self.assertEqual('This is a sample test file.', str(json[0]['record_2']),
                             msg=json)
            self.assertEqual('This is a sample test file.', str(json[0]['record_2_2']),
                             msg=json)

    def test_large_decimals(self):
        with common.get_planner() as planner:
            json = planner.scan_as_json("select num from rs.large_decimals2")
            self.assertTrue(len(json) == 6, msg=json)
            self.assertEqual('9012248907891233.020304050670',
                             str(json[0]['num']), msg=json)
            self.assertEqual('2343.999900000000', str(json[1]['num']), msg=json)
            self.assertEqual('900.000000000000', str(json[2]['num']), msg=json)
            self.assertEqual('32.440000000000', str(json[3]['num']), msg=json)
            self.assertEqual('54.230000000000', str(json[4]['num']), msg=json)
            self.assertEqual('4525.340000000000', str(json[5]['num']), msg=json)

        with common.get_planner() as planner:
            df = planner.scan_as_pandas("select num from rs.large_decimals2")
            self.assertTrue(len(df) == 6, msg=df)
            self.assertEqual('9012248907891233.020304050670',
                             str(df['num'][0]), msg=df)
            self.assertEqual('2343.999900000000', str(df['num'][1]), msg=df)
            self.assertEqual('900.000000000000', str(df['num'][2]), msg=df)
            self.assertEqual('32.440000000000', str(df['num'][3]), msg=df)
            self.assertEqual('54.230000000000', str(df['num'][4]), msg=df)
            self.assertEqual('4525.340000000000', str(df['num'][5]), msg=df)

    def test_scan_as_json_max_records(self):
        sql = "select * from okera_sample.sample"
        with common.get_planner() as planner:
            json = planner.scan_as_json(sql, max_records=1, max_client_process_count=1)
            self.assertTrue(len(json) == 1, msg='max_records not respected')
            json = planner.scan_as_json(sql, max_records=100, max_client_process_count=1)
            self.assertTrue(len(json) == 2, msg='max_records not respected')

    def test_scan_as_pandas_max_records(self):
        sql = "select * from okera_sample.sample"
        with common.get_planner() as planner:
            pd = planner.scan_as_pandas(sql, max_records=1, max_client_process_count=1)
            self.assertTrue(len(pd.index) == 1, msg='max_records not respected')
            pd = planner.scan_as_pandas(sql, max_records=100, max_client_process_count=1)
            self.assertTrue(len(pd.index) == 2, msg='max_records not respected')

    def test_scan_retry(self):
        global retry_count
        sql = "select * from okera_sample.sample"
        with common.get_planner() as planner:
            # First a sanity check
            pd = planner.scan_as_pandas(sql, max_records=1, max_client_process_count=1)
            self.assertTrue(len(pd.index) == 1, msg='test_scan_retry sanity check failed')

            # Patch scan_as_pandas to throw an IOError 2 times
            retry_count = 0
            def test_hook_retry(func_name, retries, attempt):
                if func_name != "plan":
                    return
                global retry_count
                retry_count = retry_count + 1
                if attempt < 2:
                    raise IOError('Fake Error')

            planner.test_hook_retry = test_hook_retry
            pd = planner.scan_as_pandas(sql, max_records=1, max_client_process_count=1)

            assert(retry_count == 3) # count = 2 failures + 1 success
            self.assertTrue(len(pd.index) == 1, msg='Failed to get data with retries')


if __name__ == "__main__":
    unittest.main()
