# Copyright 2017 Okera Inc. All Rights Reserved.
#
# Tests that should run on any configuration. The server auth can be specified
# as an environment variables before running this test.

# pylint: disable=no-member
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=bad-continuation
# pylint: disable=bad-indentation
import unittest

import numpy
from tzlocal import get_localzone

from okera import version, _thrift_api
from okera.tests import pycerebro_test_common as common

# The timestamp values are TZ specific, switch based on this.
# TODO: this is an awful way to do this.
TIME_ZONE = get_localzone().zone

class BasicTest(unittest.TestCase):

    def test_version(self):
        self.assertTrue(version())

    def test_connection(self):
        planner = common.get_planner()
        self.assertEqual("1.0", planner.get_protocol_version())
        planner.close()
        worker = common.get_worker()
        self.assertEqual("1.0", worker.get_protocol_version())
        worker.close()

    def test_random_host(self):
        ctx = common.get_test_context()
        host, port = ctx._OkeraContext__pick_host('abc', 123)
        self.assertEqual(host, 'abc')
        self.assertEqual(port, 123)

        host, port = ctx._OkeraContext__pick_host(['abc:234'], 123)
        self.assertEqual(host, 'abc')
        self.assertEqual(port, 234)

        host, port = ctx._OkeraContext__pick_host('abc:234', 123)
        self.assertEqual(host, 'abc')
        self.assertEqual(port, 234)

        for _ in range(0, 10):
            host, port = ctx._OkeraContext__pick_host(['abc', 'def'], 123)
            self.assertTrue(host in ['abc', 'def'])
            self.assertEqual(port, 123)

        # Test some invalid args
        with self.assertRaises(ValueError):
            ctx._OkeraContext__pick_host(None, None)
        with self.assertRaises(ValueError):
            ctx._OkeraContext__pick_host("abc:123:45", 123)
        with self.assertRaises(ValueError):
            ctx._OkeraContext__pick_host([1], 123)
        with self.assertRaises(ValueError):
            ctx._OkeraContext__pick_host(1, 123)
        with self.assertRaises(ValueError):
            ctx._OkeraContext__pick_host('123', None)

    def test_pick_host(self):
        opt = {}
        opt['PIN_HOST'] = 1

        ctx = common.get_test_context()
        host, port = ctx._OkeraContext__pick_host('abc', 123, opt)
        self.assertEqual(host, 'abc')
        self.assertEqual(port, 123)

        # Should always pick the first one
        for _ in range(0, 10):
            host, port = ctx._OkeraContext__pick_host(['abc', 'def'], 123, opt)
            self.assertTrue(host == 'abc')
            self.assertEqual(port, 123)

        network_hosts = [
            _thrift_api.TNetworkAddress("678", 3),
            _thrift_api.TNetworkAddress("456", 4)]
        for _ in range(0, 10):
            host, port = ctx._OkeraContext__pick_host(network_hosts, None, opt)
            self.assertTrue(host == '456')
            self.assertEqual(port, 4)

    def test_basic(self):
        ctx = common.get_test_context()
        # Can either be None or a token depending on the dev setup
        self.assertTrue(ctx.get_auth() is None or ctx.get_auth() == 'TOKEN')
        if ctx.get_auth() == 'TOKEN':
            self.assertTrue(ctx.get_token() is not None)

        ctx.disable_auth()
        self.assertTrue(ctx.get_auth() is None)

        ctx.enable_token_auth('ab.cd')
        self.assertEqual('TOKEN', ctx.get_auth())
        self.assertEqual('ab.cd', ctx.get_token())

        ctx.enable_token_auth('user')
        self.assertTrue(ctx.get_auth() is None)
        self.assertEqual('user', ctx._get_user())

    def test_planner(self):
        ctx = common.get_test_context()
        planner = ctx.connect()
        self.assertEqual('1.0', planner.get_protocol_version())
        planner.close()

        # Should be able to make more
        with ctx.connect() as planner:
            self.assertEqual('1.0', planner.get_protocol_version())

    def test_worker(self):
        ctx = common.get_test_context()
        worker = ctx.connect_worker()
        self.assertEqual('1.0', worker.get_protocol_version())
        worker.close()

        # Should be able to make more
        with ctx.connect_worker() as worker:
            self.assertEqual('1.0', worker.get_protocol_version())

    def test_catalog(self):
        planner = common.get_planner()
        dbs = planner.list_databases()
        self.assertTrue('okera_sample' in dbs)
        datasets = planner.list_datasets('okera_sample')
        self.assertTrue(datasets is not None)
        dataset_names = planner.list_dataset_names('okera_sample')
        self.assertTrue('okera_sample.sample' in dataset_names, msg=dataset_names)
        self.assertTrue('okera_sample.users' in dataset_names, msg=dataset_names)
        planner.close()

    def test_ddl(self):
        planner = common.get_planner()
        result = planner.execute_ddl("show databases")
        planner.close()
        print(result)
        self.assertTrue(len(result) > 3)

    def test_plan(self):
        planner = common.get_planner()
        plan = planner.plan("tpch.nation")
        self.assertEqual(1, len(plan.tasks))
        planner.close()

    def test_all_types_json(self):
        planner = common.get_planner()
        json = planner.scan_as_json("rs.alltypes")
        planner.close()
        self.assertEqual(2, len(json))
        r1 = json[0]
        r2 = json[1]
        self.assertEqual(12, len(r1))
        self.assertEqual(12, len(r2))
        self.assertEqual(True, r1['bool_col'])
        self.assertEqual(6, r2['tinyint_col'])
        self.assertEqual(1, r1['smallint_col'])
        self.assertEqual(8, r2['int_col'])
        self.assertEqual(3, r1['bigint_col'])
        self.assertEqual(10.0, r2['float_col'])
        self.assertEqual(5.0, r1['double_col'])
        self.assertEqual('world', r2['string_col'])
        self.assertEqual('vchar1', r1['varchar_col'])
        self.assertEqual('char2', r2['char_col'])
        self.assertEqual('3.1415920000', str(r1['decimal_col']))
        self.assertEqual('2016-01-01 00:00:00+00:00', str(r2['timestamp_col']))

    def test_requesting_user(self):
        planner = common.get_planner()
        json = planner.scan_as_json("rs.alltypes", requesting_user="testuser")
        planner.close()
        self.assertEqual(2, len(json))
        r1 = json[0]
        r2 = json[1]
        self.assertEqual({'int_col' : 2, 'string_col' : 'hello'}, r1)
        self.assertEqual({'int_col' : 8, 'string_col' : 'world'}, r2)

        planner = common.get_planner()
        pd = planner.scan_as_pandas("rs.alltypes", requesting_user="testuser")
        planner.close()
        self.assertEqual(2, len(pd))
        self.assertEqual(['int_col', 'string_col'], list(pd.columns))

    def test_all_types_pandas(self):
        planner = common.get_planner()
        pd = planner.scan_as_pandas("rs.alltypes")
        planner.close()
        self.assertEqual(2, len(pd))
        self.assertEqual(12, len(pd.columns))
        self.assertEqual(True, pd['bool_col'][0])
        self.assertEqual(False, pd['bool_col'][1])
        self.assertEqual(0, pd['tinyint_col'][0])
        self.assertEqual(6, pd['tinyint_col'][1])
        self.assertEqual(1, pd['smallint_col'][0])
        self.assertEqual(7, pd['smallint_col'][1])
        self.assertEqual(2, pd['int_col'][0])
        self.assertEqual(8, pd['int_col'][1])
        self.assertEqual(3, pd['bigint_col'][0])
        self.assertEqual(9, pd['bigint_col'][1])
        self.assertEqual(4.0, pd['float_col'][0])
        self.assertEqual(10.0, pd['float_col'][1])
        self.assertEqual(5.0, pd['double_col'][0])
        self.assertEqual(11.0, pd['double_col'][1])
        self.assertEqual(b'hello', pd['string_col'][0])
        self.assertEqual(b'world', pd['string_col'][1])
        self.assertEqual(b'vchar1', pd['varchar_col'][0])
        self.assertEqual(b'vchar2', pd['varchar_col'][1])
        self.assertEqual(b'char1', pd['char_col'][0])
        self.assertEqual(b'char2', pd['char_col'][1])
        self.assertEqual('3.1415920000', str(pd['decimal_col'][0]))
        self.assertEqual('1234.5678900000', str(pd['decimal_col'][1]))

        self.assertEqual('2015-01-01 00:00:00+00:00', str(pd['timestamp_col'][0]))
        self.assertEqual('2016-01-01 00:00:00+00:00', str(pd['timestamp_col'][1]))

    def test_all_types_null_pandas(self):
        planner = common.get_planner()
        pd = planner.scan_as_pandas("rs.alltypes_null")
        planner.close()
        self.assertEqual(1, len(pd))
        self.assertEqual(12, len(pd.columns))
        for i in range(0, len(pd.columns)):
            self.assertTrue(numpy.isnan(pd.iloc[0, i]), msg=pd)

    def test_all_types_empty(self):
        planner = common.get_planner()
        pd = planner.scan_as_pandas("rs.alltypes_empty")
        planner.close()
        self.assertEqual(
            ['bool_col', 'tinyint_col', 'smallint_col', 'int_col', 'bigint_col',
             'float_col', 'double_col', 'string_col', 'varchar_col', 'char_col',
             'timestamp_col', 'decimal_col'],
            list(pd.columns), msg=pd)
        self.assertEqual(0, len(pd), msg=pd)
        self.assertEqual(12, len(pd.columns), msg=pd)

    def test_all_types_null_json(self):
        planner = common.get_planner()
        json = planner.scan_as_json("rs.alltypes_null")
        planner.close()
        self.assertEqual(1, len(json), msg=json)
        self.assertEqual(12, len(json[0]), msg=json[0])
        for v in json[0]:
            self.assertTrue(json[0][v] is None, msg=json[0])

    def test_all_types_empty_json(self):
        planner = common.get_planner()
        json = planner.scan_as_json("rs.alltypes_empty")
        planner.close()
        self.assertEqual(0, len(json), msg=json)

    def test_filter_with_empty_rows_pandas(self):
        planner = common.get_planner()
        pd = planner.scan_as_pandas(
            "SELECT * FROM okera_sample.users where gender = 'lol'"
        )
        planner.close()
        self.assertEqual(0, len(pd), msg=pd)

    def test_column_order_scan_as_pandas(self):
        planner = common.get_planner()
        self.assertEqual(
            list(planner.scan_as_pandas("okera_sample.users").columns),
            ['uid', 'dob', 'gender', 'ccn'])
        self.assertEqual(
            list(planner.scan_as_pandas("select dob, uid from okera_sample.users")
                 .columns),
            ['dob', 'uid'])
        self.assertEqual(
            list(planner.scan_as_pandas("rs.alltypes_s3").columns),
            ['bool_col', 'tinyint_col', 'smallint_col', 'int_col', 'bigint_col',
             'float_col', 'double_col', 'string_col', 'varchar_col', 'char_col',
             'timestamp_col', 'decimal_col'])
        self.assertEqual(
            list(planner.scan_as_pandas(
                "select decimal_col, bigint_col from rs.alltypes_s3").columns),
            ['decimal_col', 'bigint_col'])

    def test_binary_data(self):
        with common.get_planner() as planner:
            planner.execute_ddl("create database if not exists binarydb")
            planner.execute_ddl("""
                create external table if not exists binarydb.sample (record binary)
                ROW FORMAT DELIMITED FIELDS TERMINATED BY '|' STORED AS TEXTFILE
                LOCATION 's3://cerebrodata-test/sample'""")

            df = planner.scan_as_pandas("binarydb.sample")
            self.assertEqual(2, len(df), msg=df)
            self.assertEqual(2, df['record'].count(), msg=df)
            self.assertEqual(b'This is a sample test file.', df['record'][0], msg=df)

            planner.execute_ddl("drop table binarydb.sample")
            planner.execute_ddl("drop database binarydb")

    def test_warnings(self):
        with common.get_planner() as planner:
            warnings = []
            result = planner.scan_as_json("okera_sample.sample", warnings=warnings)
            self.assertEqual(2, len(result))
            self.assertEqual(0, len(warnings))

            result = planner.scan_as_json("rs.alltypes_empty", warnings=warnings)
            self.assertEqual(0, len(result))
            self.assertEqual(1, len(warnings))
            self.assertTrue("has no data files" in warnings[0])

    def test_impersonation(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth('testuser')
        with ctx.connect() as planner:
            # Spot check a few
            dbs = []
            for r in planner.execute_ddl('show databases'):
                dbs.append(r[0])

            self.assertTrue('okera_sample' in dbs, msg=dbs)
            self.assertTrue('rs' in dbs, msg=dbs)
            self.assertFalse('customer' in dbs, msg=dbs)

            dbs2 = planner.list_databases()
            self.assertEqual(dbs, dbs2)

            tbl_names = planner.list_dataset_names('rs')
            self.assertTrue('rs.alltypes' in tbl_names, msg=tbl_names)
            self.assertTrue('rs.alltypes_s3' in tbl_names, msg=tbl_names)
            self.assertFalse('rs.s3_nation' in tbl_names, msg=tbl_names)

            tbls = planner.list_datasets('rs').tables
            self.assertEqual(len(tbl_names), len(tbls))

            result = planner.scan_as_json('okera_sample.whoami')[0]
            self.assertEqual(result['user'], 'testuser')

if __name__ == "__main__":
    unittest.main()
