import json
import unittest

tc = unittest.TestCase("__init__")


# validate if details
def assert_datamart_details(details, schema, state='active'):
    print("Datamart details:\n{}".format(details))
    tc.assertIsNotNone(details)
    tc.assertEqual(details['status']['state'], state)
    tc.assertEqual(details['database_configuration']['location']['schema'], schema)


# validate payload logging configuration details
def assert_payload_logging_configuration(payload_logging_details, dynamic_schema_update=False):
    print("Payload logging details - assert_payload_logging_configuration - \n{}".format(payload_logging_details))

    tc.assertIsNotNone(payload_logging_details)
    tc.assertTrue(payload_logging_details['enabled'])
    if dynamic_schema_update:
        tc.assertTrue(payload_logging_details['parameters']['dynamic_schema_update'])


# validate performance monitoring configuration details
def assert_performance_monitoring_configuration(performance_monitoring_details):
    print("Performance monitoring details - assert_performance_monitoring_configuration - \n{}".format(performance_monitoring_details))

    tc.assertIsNotNone(performance_monitoring_details)
    tc.assertTrue(performance_monitoring_details['enabled'])


# validate quality monitoring configuration details
def assert_quality_monitoring_configuration(quality_monitoring_details):
    print("Performance monitoring details - assert_performance_monitoring_configuration - \n{}".format(quality_monitoring_details))

    tc.assertIsNotNone(quality_monitoring_details)
    tc.assertTrue(quality_monitoring_details['enabled'])


def assert_payload_logging_pandas_table_content(pandas_table_content, scoring_records=None):
    print("Payload pandas table content - assert_payload_logging_pandas_table_content -\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    if scoring_records is not None:
        tc.assertEqual(scoring_records, rows , msg="Number of scored records ({}) is different than logged in table ({})".format(scoring_records, rows))


def assert_payload_logging_python_table_content(python_table_content, fields=[]):
    print("Payload python table content - assert_payload_logging_python_table_content -\n{}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


def assert_performance_monitoring_pandas_table_content(pandas_table_content):
    print("Payload pandas table content - assert_performance_monitoring_pandas_table_content -\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    tc.assertGreater(rows, 0, msg="Performance monitoring table is empty.")


def assert_performance_monitoring_python_table_content(python_table_content, fields=[]):
    print("Payload python table content - assert_performance_monitoring_python_table_content -\n{}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


def assert_quality_monitoring_pandas_table_content(pandas_table_content):
    print("Quality pandas table content - assert_quality_monitoring_pandas_table_content -\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    tc.assertGreater(rows, 0, msg="Quality monitoring table is empty.")


def assert_quality_monitoring_python_table_content(python_table_content, fields=[]):
    print("Quality python table content - assert_quality_monitoring_python_table_content -\n{}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


def assert_feedback_pandas_table_content(pandas_table_content, feedback_records=None):
    print("Feedback pandas table content - assert_feedback_pandas_table_content -\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    if feedback_records is not None:
        tc.assertEqual(feedback_records, rows, msg="Number of records send to feedback ({}) is different than logged in table ({})".format(feedback_records, rows))


def assert_feedback_python_table_content(python_table_content, fields=[]):
    print("Feedback python table content - assert_feedback_python_table_content -\n{}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


# validate if monitors are enabled
def assert_monitors_enablement(subscription_details, payload=False, performance=False, quality=False, fairness=False, explainability=False):
    print("Subscription details - assert_monitors_enablement - \n{}".format(subscription_details))

    for configuration in subscription_details['entity']['configurations']:
        if configuration['type'] == 'payload_logging':
            tc.assertEqual(payload, configuration['enabled'])
        elif configuration['type'] == 'performance_monitoring':
            tc.assertEqual(performance, configuration['enabled'])
        elif configuration['type'] == 'quality_monitoring':
            tc.assertEqual(quality, configuration['enabled'])
        elif configuration['type'] == 'fairness_monitoring':
            tc.assertEqual(fairness, configuration['enabled'])
        elif configuration['type'] == 'explainability':
            tc.assertEqual(explainability, configuration['enabled'])


def assert_performance_metrics(metrics):
    print("Performance metrics - assert_performance_metrics -\n{}".format(metrics))
    tc.assertGreater(len(metrics['metrics']), 0, msg="Performance metrics are empty.")


def assert_deployment_metrics(metrics):
    print("Deployment metrics - assert_deployment_metrics -\n{}".format(metrics))
    tc.assertGreater(len(metrics['deployment_metrics']), 0, msg="Deployment metrics are empty.")