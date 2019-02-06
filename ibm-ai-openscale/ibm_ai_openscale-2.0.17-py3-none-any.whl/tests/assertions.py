import json
import unittest

tc = unittest.TestCase("__init__")


def assert_datamart_details(details, schema, state='active'):
    print("** assert_datamart_details **\nDatamart details: {}".format(details))
    tc.assertIsNotNone(details)
    tc.assertEqual(details['status']['state'], state)
    tc.assertEqual(details['database_configuration']['location']['schema'], schema)


def assert_subscription_details(subscription_details, asset_uid=None, no_deployments=None, text_included="", enabled_monitors=[]):
    print("** assert_subscription_details **\nSubscription details: {}".format(subscription_details))

    for configuration in subscription_details['entity']['configurations']:
        if configuration['type'] in enabled_monitors:
            tc.assertTrue(configuration['enabled'], msg="{} is disabled.".format(configuration['type']))

    if asset_uid is not None:
        tc.assertEqual(asset_uid, subscription_details['entity']['asset']['asset_id'])

    if no_deployments is not None:
        tc.assertEqual(no_deployments, len(subscription_details['entity']['deployments']))

    tc.assertIn(text_included, str(subscription_details))


def assert_payload_logging_configuration(payload_logging_details, dynamic_schema_update=False):
    print("** assert_payload_logging_configuration **\nPayload logging details: {}".format(payload_logging_details))

    tc.assertIsNotNone(payload_logging_details)
    tc.assertTrue(payload_logging_details['enabled'])
    if dynamic_schema_update:
        tc.assertTrue(payload_logging_details['parameters']['dynamic_schema_update'], msg="Dynamic schema update is disabled.")


def assert_performance_monitoring_configuration(performance_monitoring_details):
    print("** assert_performance_monitoring_configuration **\nPerformance monitoring details: {}".format(performance_monitoring_details))

    tc.assertIsNotNone(performance_monitoring_details)
    tc.assertTrue(performance_monitoring_details['enabled'])


def assert_quality_monitoring_configuration(quality_monitoring_details):
    print("** assert_quality_monitoring_configuration **\nQuality monitoring details: {}".format(quality_monitoring_details))

    tc.assertIsNotNone(quality_monitoring_details)
    tc.assertTrue(quality_monitoring_details['enabled'])


def assert_explainability_configuration(explainability_details):
    print("** assert_explainability_configuration **\nExplainability details: {}".format(explainability_details))

    tc.assertIsNotNone(explainability_details)
    tc.assertTrue(explainability_details['enabled'])


def assert_fairness_configuration(fairness_monitoring_details):
    print("** assert_fairness_configuration **\nFariness monitoring details: {}".format(fairness_monitoring_details))

    tc.assertIsNotNone(fairness_monitoring_details)
    tc.assertTrue(fairness_monitoring_details['enabled'])


def assert_payload_logging_pandas_table_content(pandas_table_content, scoring_records=None):
    print("** assert_payload_logging_pandas_table_content **\nPayload pandas table content:\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    if scoring_records is not None:
        tc.assertEqual(scoring_records, rows , msg="Number of scored records ({}) is different than logged in table ({})".format(scoring_records, rows))


def assert_payload_logging_python_table_content(python_table_content, fields=[]):
    print("** assert_payload_logging_python_table_content **\nPayload python table content: {}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


def assert_performance_monitoring_pandas_table_content(pandas_table_content):
    print("** assert_performance_monitoring_pandas_table_content **\nPerformance pandas table content:\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    tc.assertGreater(rows, 0, msg="Performance monitoring table is empty.")


def assert_performance_monitoring_python_table_content(python_table_content, fields=[]):
    print("** assert_performance_monitoring_python_table_content **\nPerformance python table content: {}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


def assert_quality_monitoring_pandas_table_content(pandas_table_content):
    print("** assert_quality_monitoring_pandas_table_content **\nQuality pandas table content:\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    tc.assertGreater(rows, 0, msg="Quality monitoring table is empty.")


def assert_quality_monitoring_python_table_content(python_table_content, fields=[]):
    print("** assert_quality_monitoring_python_table_content **\nQuality python table content: {}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


def assert_explainability_pandas_table_content(pandas_table_content):
    print("** assert_explainability_pandas_table_content **\nExplainability pandas table content:\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    tc.assertGreater(rows, 0, msg="Explainability table is empty.")


def assert_explainability_python_table_content(python_table_content, fields=[]):
    print("** assert_explainability_python_table_content **\nExplainability python table content: {}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


def assert_fairness_monitoring_pandas_table_content(pandas_table_content):
    print("** assert_fairness_monitoring_pandas_table_content **\nFairness pandas table content:\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    tc.assertGreater(rows, 0, msg="Fairness monitoring table is empty.")


def assert_fairness_monitoring_python_table_content(python_table_content, fields=[]):
    print("** assert_fairness_monitoring_python_table_content **\nFairness python table content: {}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


def assert_feedback_pandas_table_content(pandas_table_content, feedback_records=None):
    print("** assert_feedback_pandas_table_content **\nFeedback pandas table content:\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    if feedback_records is not None:
        tc.assertEqual(feedback_records, rows, msg="Number of records send to feedback ({}) is different than logged in table ({})".format(feedback_records, rows))


def assert_feedback_python_table_content(python_table_content, fields=[]):
    print("** assert_feedback_python_table_content **\nFeedback python table content:{}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


def assert_monitors_enablement(subscription_details, payload=False, performance=False, quality=False, fairness=False, explainability=False):
    print("** assert_monitors_enablement **\nSubscription details: {}".format(subscription_details))

    for configuration in subscription_details['entity']['configurations']:
        if configuration['type'] == 'payload_logging':
            tc.assertEqual(payload, configuration['enabled'], msg="Payload logging is {}. Assert expectation: {}".format(configuration['enabled'], payload))
        elif configuration['type'] == 'performance_monitoring':
            tc.assertEqual(performance, configuration['enabled'], msg="Performance monitoring is {}. Assert expectation: {}".format(configuration['enabled'], performance))
        elif configuration['type'] == 'quality_monitoring':
            tc.assertEqual(quality, configuration['enabled'], msg="Quality monitoring is {}. Assert expectation: {}".format(configuration['enabled'], quality))
        elif configuration['type'] == 'fairness_monitoring':
            tc.assertEqual(fairness, configuration['enabled'], msg="Fairness monitoring is {}. Assert expectation: {}".format(configuration['enabled'], fairness))
        elif configuration['type'] == 'explainability':
            tc.assertEqual(explainability, configuration['enabled'], msg="Explainability is {}. Assert expectation: {}".format(configuration['enabled'], explainability))


def assert_explainability_run(explainability_run_details):
    print("** assert_explainability_run **\nExplainability run details: {}".format(explainability_run_details))

    tc.assertIsNotNone(explainability_run_details)
    statuses = explainability_run_details['entity']['status']

    for status in statuses.values():
        tc.assertEqual("finished", status, msg="Explainability run failed in single step.")


def assert_fairness_run(fairness_run_details):
    print("** assert_fairness_run **\nFairness run details: {}".format(fairness_run_details))

    tc.assertIsNotNone(fairness_run_details)
    tc.assertEqual('FINISHED', fairness_run_details['entity']['parameters']['last_run_status'])
    tc.assertEqual('bias run is successful', fairness_run_details['entity']['parameters']['last_run_message'])


def assert_performance_metrics(metrics):
    print("** assert_performance_metrics **\nPerformance metrics: {}".format(metrics))
    tc.assertGreater(len(metrics['metrics']), 0, msg="Performance metrics are empty.")


def assert_deployment_metrics(metrics):
    print("** assert_deployment_metrics **\nDeployment metrics: {}".format(metrics))
    tc.assertGreater(len(metrics['deployment_metrics']), 0, msg="Deployment metrics are empty.")
