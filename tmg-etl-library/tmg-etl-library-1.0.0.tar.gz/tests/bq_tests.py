import unittest
from tmg_etl_library.components.databases import bq
from tmg_etl_library.components.locals.csv import CSVFile
from tmg_etl_library.components.config import *
from google.cloud import bigquery
import os
from google.api_core.exceptions import NotFound
from tmg_etl_library.cloud_logger import cloud_logger

import time


TEST_PROJECT = 'tmg-plat-dev'
TEST_DATASET = 'tmg_etl_library_tests'
log = cloud_logger.Logger("test-app", "logger-name", "tmg-plat-dev")

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
# test helper file definition path
ADDITIONAL_FILES = '{0}/bq_tests_files'.format(MODULE_PATH)

def setUpModule():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/google-keys/dev-pipeline.json'
    client = bigquery.Client(project='tmg-plat-dev')
    test_dataset = client.dataset('tmg_etl_library_tests')
    try:
        gbq_dataset = client.get_dataset(test_dataset)
        # Gets to next line if NotFound exception not hit
        gbq_tables = client.list_tables(test_dataset)
        for table in gbq_tables:
            bq_table = gbq_dataset.table(table.table_id)
            client.delete_table(bq_table)
        client.delete_dataset(test_dataset)
    except NotFound:
        pass
    finally:
        client.create_dataset(test_dataset)

def tearDownModule():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/google-keys/dev-pipeline.json'
    client = bigquery.Client(project='tmg-plat-dev')
    test_dataset = client.dataset('tmg_etl_library_tests')

    gbq_dataset = client.get_dataset(test_dataset)
    gbq_tables = client.list_tables(test_dataset)
    for table in gbq_tables:
        bq_table = gbq_dataset.table(table.table_id)
        client.delete_table(bq_table)

    client.delete_dataset(test_dataset)


def delete_tables_in_dataset():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/google-keys/dev-pipeline.json'
    client = bigquery.Client(project='tmg-plat-dev')
    test_dataset = client.dataset('tmg_etl_library_tests')

    gbq_dataset = client.get_dataset(test_dataset)
    gbq_tables = client.list_tables(test_dataset)
    for table in gbq_tables:
        bq_table = gbq_dataset.table(table.table_id)
        client.delete_table(bq_table)


class Test_table_exists(unittest.TestCase):

    def setUp(self):
        self.tmg_bq_client = bq.BQClient(log=log, project='tmg-plat-dev')
        self.gbq_client = self.tmg_bq_client.client
        self.test_dataset = self.gbq_client.dataset('tmg_etl_library_tests')

    def test_table_does_exist(self):
        table_1 = self.test_dataset.table('table_exists_1')
        self.gbq_client.create_table(table_1)
        tmg_table_1 = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'table_exists_1')

        self.assertEqual(self.tmg_bq_client.table_exists(tmg_table_1), True)

    def test_table_does_not_exist(self):
        tmg_table_2 = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'table_exists_2')
        self.assertEqual(self.tmg_bq_client.table_exists(tmg_table_2), False)


class Test_list_tables(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        delete_tables_in_dataset()

    def setUp(self):
        self.tmg_bq_client = bq.BQClient(log=log, project='tmg-plat-dev')
        self.gbq_client = self.tmg_bq_client.client
        self.test_dataset = self.gbq_client.dataset('tmg_etl_library_tests')

    def test_list_tables(self):
        table_names = ['list_table_a', 'list_table_b', 'list_table_c']
        for table in table_names:
            table_to_create = self.test_dataset.table(table)
            self.gbq_client.create_table(table_to_create)

        # Have to take String Representations because the instances will never be identical - Investigate further
        expected = [str(bq.BQTable(project=TEST_PROJECT, dataset=TEST_DATASET, name=table_name)) for table_name in
                    table_names]
        response = self.tmg_bq_client.list_tables(TEST_PROJECT, TEST_DATASET)
        response.sort(key=lambda x: x.name)
        response = [str(t) for t in response]

        self.assertEqual(expected, response)

    def test_list_tables_regex(self):
        table_names = ['list_table_1_a', 'list_table_2_', 'list_table_no_number']
        for table in table_names:
            table_to_create = self.test_dataset.table(table)
            self.gbq_client.create_table(table_to_create)
        expected_table_names = ['list_table_1_a', 'list_table_2_']
        expected = [str(bq.BQTable(project=TEST_PROJECT, dataset=TEST_DATASET, name=table_name)) for table_name in
                    expected_table_names]
        response = self.tmg_bq_client.list_tables(TEST_PROJECT, TEST_DATASET, table_regex='.*[0-9].*')
        response.sort(key=lambda x: x.name)
        response = [str(t) for t in response]

        self.assertEqual(expected, response)

class Test_delete_tables(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        delete_tables_in_dataset()

    def setUp(self):
        self.tmg_bq_client = bq.BQClient(log=log, project='tmg-plat-dev')
        self.gbq_client = self.tmg_bq_client.client
        self.test_dataset = self.gbq_client.dataset('tmg_etl_library_tests')

    # Using table_exists which has already been tested above
    def test_delete_tables_list(self):
        table_names = ['delete_table_a', 'delete_table_b', 'delete_table_c']
        for table in table_names:
            table_to_create = self.test_dataset.table(table)
            self.gbq_client.create_table(table_to_create)

        tables_to_delete = ['delete_table_a', 'delete_table_b']
        BQTables_to_delete = [bq.BQTable(project=TEST_PROJECT, dataset=TEST_DATASET, name=table_name) for table_name in
                              tables_to_delete]

        self.tmg_bq_client.delete_tables(BQTables_to_delete)
        table_a = bq.BQTable(project=TEST_PROJECT, dataset=TEST_DATASET, name='delete_table_a')
        table_b = bq.BQTable(project=TEST_PROJECT, dataset=TEST_DATASET, name='delete_table_b')
        table_c = bq.BQTable(project=TEST_PROJECT, dataset=TEST_DATASET, name='delete_table_c')

        self.assertFalse(self.tmg_bq_client.table_exists(table_a))
        self.assertFalse(self.tmg_bq_client.table_exists(table_b))
        self.assertTrue(self.tmg_bq_client.table_exists(table_c))


class Test_create_table(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        delete_tables_in_dataset()

    def setUp(self):
        self.tmg_bq_client = bq.BQClient(log=log, project='tmg-plat-dev')
        self.gbq_client = self.tmg_bq_client.client
        self.test_dataset = self.gbq_client.dataset(TEST_DATASET)
        self.create_table_config = bq.BQTableConfig()

    def test_create_table_basic(self):
        self.create_table_config.force_dataset_creation = True
        self.create_table_config.force_table_creation = True
        table1 = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'create_table_1')

        schema1 = [{'mode': 'NULLABLE', 'name': 'PID', 'type': 'STRING'},
                    {'mode': 'NULLABLE', 'name': 'Gender', 'type': 'STRING'},
                    {'mode': 'NULLABLE', 'name': 'DOB', 'type': 'DATE'},
                    {'mode': 'NULLABLE', 'name': 'AcornCategoryDesc', 'type': 'STRING'},
                    {'mode': 'NULLABLE', 'name': 'AcornGroupDesc', 'type': 'STRING'}]

        table1.schema = schema1

        function_response = self.tmg_bq_client.create_table(table1, self.create_table_config)


        table = self.test_dataset.table('create_table_1')
        try:
            table = self.gbq_client.get_table(table)
        except NotFound:
            table = None

        self.assertIsNotNone(table)

        self.assertEqual(bq.BQTable(TEST_PROJECT, TEST_DATASET, 'create_table_1').__dict__, function_response.__dict__)


    def test_force_table_creation(self):
        self.create_table_config.force_dataset_creation = True
        self.create_table_config.force_table_creation = False
        table2 = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'create_table_2')

        schema2 = [{'mode': 'NULLABLE', 'name': 'PID', 'type': 'STRING'},
                   {'mode': 'NULLABLE', 'name': 'DOB', 'type': 'DATE'},
                   {'mode': 'NULLABLE', 'name': 'AcornGroupDesc', 'type': 'STRING'}]

        table2.schema = schema2

        with self.assertRaises(Exception):
            self.tmg_bq_client.create_table(table2, self.create_table_config)

    def test_table_expiry(self):
        self.create_table_config.force_dataset_creation = True
        self.create_table_config.force_table_creation = True
        table3 = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'create_table_3')

        schema3 = [{'mode': 'NULLABLE', 'name': 'PID', 'type': 'STRING'},
                   {'mode': 'NULLABLE', 'name': 'DOB', 'type': 'DATE'},
                   {'mode': 'NULLABLE', 'name': 'AcornGroupDesc', 'type': 'STRING'}]

        table3.schema = schema3
        table3.expiry = 15

        self.tmg_bq_client.create_table(table3, self.create_table_config)

        table = self.test_dataset.table('create_table_3')
        table = self.gbq_client.get_table(table)

        self.assertIsNotNone(table.expires)


    def test_table_partitioned_field(self):
        self.create_table_config.force_dataset_creation = True
        self.create_table_config.force_table_creation = True
        table4 = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'create_table_4')

        schema4 = [{'mode': 'NULLABLE', 'name': 'PID', 'type': 'STRING'},
                   {'mode': 'NULLABLE', 'name': 'DOB', 'type': 'DATE'},
                   {'mode': 'NULLABLE', 'name': 'AcornGroupDesc', 'type': 'STRING'}]

        table4.schema = schema4
        table4.partitioned_field = 'DOB'

        self.tmg_bq_client.create_table(table4, self.create_table_config)

        table = self.test_dataset.table('create_table_4')
        table = self.gbq_client.get_table(table)

        self.assertEqual(table.time_partitioning.field, 'DOB')


class Test_insert_csv(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        delete_tables_in_dataset()

    def setUp(self):
        self.tmg_bq_client = bq.BQClient(log=log, project='tmg-plat-dev')
        self.gbq_client = self.tmg_bq_client.client
        self.test_dataset = self.gbq_client.dataset(TEST_DATASET)
        self.insert_csv_config = CSVTOBQConfig()

    def test_insert_csv(self):
        csv_file_1 = CSVFile('insert_csv1.csv', ADDITIONAL_FILES, delimiter=',')
        table = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'insert_table1')
        schema = [{'mode': 'NULLABLE', 'name': 'one', 'type': 'STRING'},
                   {'mode': 'NULLABLE', 'name': 'two', 'type': 'STRING'},
                   {'mode': 'NULLABLE', 'name': 'three', 'type': 'STRING'},
                   {'mode': 'NULLABLE', 'name': 'four', 'type': 'STRING'}]
        table.schema = schema

        self.tmg_bq_client.insert_csv(csv_file_1, table, self.insert_csv_config)

    def test_insert_csv_append(self):
        self.insert_csv_config.write_disposition = 'WRITE_APPEND'
        csv_file_1 = CSVFile('insert_csv1.csv', ADDITIONAL_FILES, delimiter=',')
        table = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'insert_table1')
        schema = [{'mode': 'NULLABLE', 'name': 'one', 'type': 'STRING'},
                  {'mode': 'NULLABLE', 'name': 'two', 'type': 'STRING'},
                  {'mode': 'NULLABLE', 'name': 'three', 'type': 'STRING'},
                  {'mode': 'NULLABLE', 'name': 'four', 'type': 'STRING'}]
        table.schema = schema

        self.tmg_bq_client.insert_csv(csv_file_1, table, self.insert_csv_config)


class Test_query_to_file(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        delete_tables_in_dataset()

    def setUp(self):
        self.tmg_bq_client = bq.BQClient(log=log, project='tmg-plat-dev')
        self.gbq_client = self.tmg_bq_client.client
        self.test_dataset = self.gbq_client.dataset(TEST_DATASET)
        self.query_to_file_config = BQTOCSVConfig()

    def test_query_to_file_legacy(self):
        self.query_to_file_config.use_legacy_sql = True
        csv_file_2 = CSVFile('insert_csv2.csv', ADDITIONAL_FILES, delimiter=':')
        query = 'SELECT accept_language, browser, browser_height, color, curr_factor FROM [tmg-plat-dev:adobe_desktop_edition_logs.desktop_hitlog_extended_20180122] limit 50'

        self.tmg_bq_client.query_to_file(query, csv_file_2, self.query_to_file_config)

    def test_query_to_file_standard(self):
        self.query_to_file_config.use_legacy_sql = False
        csv_file_2 = CSVFile('insert_csv3.csv', ADDITIONAL_FILES, delimiter=':')
        query = 'SELECT accept_language, browser, browser_height, color, curr_factor FROM `tmg-plat-dev.adobe_desktop_edition_logs.desktop_hitlog_extended_20180122` limit 50'

        self.tmg_bq_client.query_to_file(query, csv_file_2, self.query_to_file_config)


class Test_run_query(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        delete_tables_in_dataset()

    def setUp(self):
        self.tmg_bq_client = bq.BQClient(log=log, project='tmg-plat-dev')
        self.gbq_client = self.tmg_bq_client.client
        self.test_dataset = self.gbq_client.dataset(TEST_DATASET)

    def test_query_to_table(self):
        table = bq.BQTable(project=TEST_PROJECT, dataset=TEST_DATASET, name='query_table1')
        table.schema = [{'mode': 'NULLABLE', 'name': 'adpoint_campaign_id', 'type': 'INTEGER'},
                        {'mode': 'NULLABLE', 'name': 'campaign_name', 'type': 'STRING'},
                        {'mode': 'NULLABLE', 'name': 'agency_name', 'type': 'STRING'},
                        {'mode': 'NULLABLE', 'name': 'start_date', 'type': 'INTEGER'},
                        {'mode': 'NULLABLE', 'name': 'end_date', 'type': 'INTEGER'},
                        {'mode': 'NULLABLE', 'name': 'sales_rep_name', 'type': 'STRING'}]
        query = 'SELECT adpoint_campaign_id, campaign_name, agency_name, start_date, end_date, sales_rep_name FROM `tmg-plat-dev.nick_dev.query_2b` LIMIT 100'
        self.tmg_bq_client.run_query(query=query, destination=table)

    def test_query_to_schemaless_table(self):
        table = bq.BQTable(project=TEST_PROJECT, dataset=TEST_DATASET, name='query_table2')
        query = 'SELECT adpoint_campaign_id, campaign_name, agency_name, start_date, end_date, sales_rep_name FROM `tmg-plat-dev.nick_dev.query_2b` LIMIT 100'
        self.tmg_bq_client.run_query(query=query, destination=table)

    def test_query_to_partitioned_table(self):
        table = bq.BQTable(project=TEST_PROJECT, dataset=TEST_DATASET, name='query_table3')
        table.partitioned_field = 'headline_last_update'
        query = 'SELECT campaign, url, pagename, headline, source, headline_last_update FROM `tmg-plat-dev.nick_dev.dim_spark_campaigns_urls_0323` LIMIT 1000'
        self.tmg_bq_client.run_query(query=query, destination=table)

    def test_iterator_response(self):
        query = 'SELECT adpoint_campaign_id, campaign_name, agency_name, start_date, end_date, sales_rep_name FROM `tmg-plat-dev.nick_dev.query_2b` LIMIT 100'
        iterator = self.tmg_bq_client.run_query(query=query)

    def test_async_query(self):
        timebefore = time.time()
        query = 'SELECT * FROM `tmg-plat-dev.adobe_desktop_edition_logs.desktop_hitlog_extended_20180122` LIMIT 10000'
        self.tmg_bq_client.run_query(query=query, async_query=True)
        timeafter = time.time()

        seconds_difference = timeafter - timebefore

        self.assertLess(seconds_difference, 2)

    def test_formatted_query_fp(self):
        query_fp = '{direc}/{file}'.format(direc=ADDITIONAL_FILES, file='run_query_fp.sql')
        params = {'cols': 'channel, domain, browser', 'limit': 100}
        self.tmg_bq_client.run_query(query_file_name=query_fp, query_params=params)


class Test_get_table_ref(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        delete_tables_in_dataset()

    def setUp(self):
        self.tmg_bq_client = bq.BQClient(log=log, project='tmg-plat-dev')
        self.gbq_client = self.tmg_bq_client.client
        self.test_dataset = self.gbq_client.dataset(TEST_DATASET)

    def test_valid_dataset(self):
        table = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'table_ref1')

        expected_response = self.test_dataset.table(table_id='table_ref1')
        response = self.tmg_bq_client.get_table_ref(table)

        self.assertEqual(expected_response.__dict__, response.__dict__)


class Test_update_schema(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        delete_tables_in_dataset()
        client = bq.BQClient(log=log, project='tmg-plat-dev')
        table1 = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'update_schema_1')
        table1.schema = [{'mode': 'NULLABLE', 'name': 'adpoint_campaign_id', 'type': 'INTEGER'},
                         {'mode': 'NULLABLE', 'name': 'campaign_name', 'type': 'STRING'},
                         {'mode': 'NULLABLE', 'name': 'agency_name', 'type': 'STRING'},
                         {'mode': 'NULLABLE', 'name': 'sales_rep_name', 'type': 'STRING'}]
        table2 = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'update_schema_2')
        table2.schema = [{'mode': 'NULLABLE', 'name': 'adpoint_campaign_id', 'type': 'INTEGER'},
                         {'mode': 'NULLABLE', 'name': 'campaign_name', 'type': 'STRING'},
                         {'mode': 'NULLABLE', 'name': 'agency_name', 'type': 'STRING'},
                         {'mode': 'NULLABLE', 'name': 'start_date', 'type': 'INTEGER'},
                         {'mode': 'NULLABLE', 'name': 'end_date', 'type': 'INTEGER'},
                         {'mode': 'NULLABLE', 'name': 'sales_rep_name', 'type': 'STRING'}]

        client.create_table(table1)
        client.create_table(table2)

    def setUp(self):
        self.tmg_bq_client = bq.BQClient(log=log, project='tmg-plat-dev')
        self.gbq_client = self.tmg_bq_client.client
        self.test_dataset = self.gbq_client.dataset(TEST_DATASET)

    def test_valid_update(self):
        table_to_update = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'update_schema_1')
        new_schema = [{'mode': 'NULLABLE', 'name': 'adpoint_campaign_id', 'type': 'INTEGER'},
                      {'mode': 'NULLABLE', 'name': 'campaign_name', 'type': 'STRING'},
                      {'mode': 'NULLABLE', 'name': 'agency_name', 'type': 'STRING'},
                      {'mode': 'NULLABLE', 'name': 'sales_rep_name', 'type': 'STRING'},
                      {'mode': 'NULLABLE', 'name': 'start_date', 'type': 'INTEGER'},
                      {'mode': 'NULLABLE', 'name': 'end_date', 'type': 'INTEGER'},
                      ]
        table_to_update.schema = new_schema
        self.tmg_bq_client.update_schema(table_to_update)

    def test_invalid_update_losing_cols(self):
        table_to_update = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'update_schema_2')
        new_schema = [{'mode': 'NULLABLE', 'name': 'adpoint_campaign_id', 'type': 'INTEGER'},
                      {'mode': 'NULLABLE', 'name': 'campaign_name', 'type': 'STRING'}]
        table_to_update.schema = new_schema
        with self.assertRaises(Exception):
            self.tmg_bq_client.update_schema(table_to_update)


class Test_copy_tables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        delete_tables_in_dataset()
        client = bq.BQClient(log=log, project='tmg-plat-dev')
        table1 = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'copy_table1')
        table1.schema = [{'mode': 'NULLABLE', 'name': 'adpoint_campaign_id', 'type': 'INTEGER'},
                         {'mode': 'NULLABLE', 'name': 'campaign_name', 'type': 'STRING'},
                         {'mode': 'NULLABLE', 'name': 'agency_name', 'type': 'STRING'},
                         {'mode': 'NULLABLE', 'name': 'sales_rep_name', 'type': 'STRING'}]
        table2 = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'copy_table2')
        table2.schema = [{'mode': 'NULLABLE', 'name': 'adpoint_campaign_id', 'type': 'INTEGER'},
                         {'mode': 'NULLABLE', 'name': 'campaign_name', 'type': 'STRING'},
                         {'mode': 'NULLABLE', 'name': 'agency_name', 'type': 'STRING'},
                         {'mode': 'NULLABLE', 'name': 'start_date', 'type': 'INTEGER'},
                         {'mode': 'NULLABLE', 'name': 'end_date', 'type': 'INTEGER'},
                         {'mode': 'NULLABLE', 'name': 'sales_rep_name', 'type': 'STRING'}]
        client.create_table(table1)
        client.create_table(table2)

    def setUp(self):
        self.tmg_bq_client = bq.BQClient(log=log, project='tmg-plat-dev')
        self.gbq_client = self.tmg_bq_client.client
        self.test_dataset = self.gbq_client.dataset(TEST_DATASET)

    def test_copy_one(self):
        source = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'copy_table1')
        target = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'copy_table1_new')
        self.tmg_bq_client.copy_tables(source=source, target=target, copy_list=[])

    def test_copy_append(self):
        config = BQTOBQConfig()
        config.write_disposition = 'WRITE_APPEND'
        source = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'copy_table2')
        target = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'copy_table2_new')
        self.tmg_bq_client.copy_tables(source=source, target=target, config=config)

    def test_copy_multiple(self):
        table1 = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'copy_table1')
        table2 = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'copy_table2')

        table1_target = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'copy_table_mapping_1')
        table2_target = bq.BQTable(TEST_PROJECT, TEST_DATASET, 'copy_table_mapping_2')

        mappings = [{'source': table1, 'target': table1_target}, {'source': table2, 'target': table2_target}]

        self.tmg_bq_client.copy_tables(copy_list=mappings)


class Test_wait_for_queries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        delete_tables_in_dataset()

    def setUp(self):
        self.tmg_bq_client = bq.BQClient(log=log, project='tmg-plat-dev')
        self.gbq_client = self.tmg_bq_client.client
        self.test_dataset = self.gbq_client.dataset(TEST_DATASET)

    def test_valid_queries(self):

        time_before_qs = time.time()

        q1 = self.gbq_client.query(
            'SELECT * FROM `tmg-plat-dev.adobe_desktop_edition_logs.desktop_hitlog_extended_20180122` LIMIT 10000')
        q2 = self.gbq_client.query(
            'SELECT * FROM `tmg-plat-dev.apple_news_metrics.applenews_lookup_daily_snapshot_20181001` LIMIT 1000')
        q3 = self.gbq_client.query(
            'SELECT * FROM `tmg-plat-dev.adobe_newsapp_logs.newsapp_hitlog_extended_20180101` LIMIT 10000')
        q4 = self.gbq_client.query(
            'SELECT * FROM `tmg-plat-dev.dfp_logs.NetworkImpressions_20181013` LIMIT 1000')

        time_after_qs = time.time()

        queries = [q1, q2, q3, q4]

        self.tmg_bq_client.wait_for_queries(queries)

        time_after_wait = time.time()

        print('Seconds between before queries and after queries: %s' % str(int(time_after_qs - time_before_qs)))
        print('Seconds between after queries and after wait: %s' % str(int(time_after_wait - time_after_qs)))


    def test_invalid_query_type(self):
        q1 = self.gbq_client.query(
            'SELECT * FROM `tmg-plat-dev.adobe_desktop_edition_logs.desktop_hitlog_extended_20180122` LIMIT 10000')
        q2 = self.gbq_client.query(
            'SELECT * FROM `tmg-plat-dev.apple_news_metrics.applenews_lookup_daily_snapshot_20181001` LIMIT 1000')

        queries = [q1.job_id, q2]

        with self.assertRaises(TypeError):
            self.tmg_bq_client.wait_for_queries(queries)

class Test_full_table_to_file(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        delete_tables_in_dataset()

    def setUp(self):
        self.tmg_bq_client = bq.BQClient(log=log, project='tmg-plat-dev')
        self.gbq_client = self.tmg_bq_client.client
        self.test_dataset = self.gbq_client.dataset(TEST_DATASET)
        self.full_table_to_file_config = BQTOCSVConfig()

    def test_full_table_default_settings(self):
        table = bq.BQTable('tmg-plat-dev', 'shared_facts_and_dimensions', 'dim_spark_campaigns')
        csv = CSVFile('full_table_1.csv', ADDITIONAL_FILES, delimiter='>')

        self.tmg_bq_client.full_table_to_file(table, csv, self.full_table_to_file_config)

    def test_full_table_gs_specific(self):
        table = bq.BQTable('tmg-plat-dev', 'shared_facts_and_dimensions', 'dim_geography')
        csv = CSVFile('full_table_2.csv', ADDITIONAL_FILES, delimiter='§')
        self.full_table_to_file_config.gs_bucket = 'tmg-etl-tests'
        self.full_table_to_file_config.gs_filename = 'full_table2'
        self.full_table_to_file_config.storage_retention = True

        self.tmg_bq_client.full_table_to_file(table, csv, self.full_table_to_file_config)

    def test_full_table_headers(self):
        table = bq.BQTable('tmg-plat-dev', 'shared_facts_and_dimensions', 'dim_page_type')
        csv = CSVFile('full_table_3.csv', ADDITIONAL_FILES, delimiter='|')
        self.full_table_to_file_config.print_header = True

        self.tmg_bq_client.full_table_to_file(table, csv, self.full_table_to_file_config)



    # # def test_large_table_to_file(self):
    # #     # This test was able to export the table to storage and begin copying the CSVs but it is about 40gb so stopped it
    # #     table = bq.BQTable('tmg-plat-dev', 'adobe_desktop_edition_logs', 'desktop_hitlog_extended_20180122')
    # #     csv = CSVFile('large_full_table.csv', ADDITIONAL_FILES, delimiter='§')
    # #     self.full_table_to_file_config.gs_bucket = 'tmg-etl-tests'
    # #     self.full_table_to_file_config.gs_filename = 'large_table_tcuk_test*'
    # #     self.full_table_to_file_config.storage_retention = True
    # #
    # #     self.tmg_bq_client.full_table_to_file(table, csv, self.full_table_to_file_config)


if __name__ == '__main__':
    unittest.main()
