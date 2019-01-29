import requests
import time
from pytest_bdd import scenario, given, when, then
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes import PayloadRecord
from ibm_ai_openscale.supporting_classes.enums import InputDataType, ProblemType
from nonfunction.fixtures import *
import nonfunction.common_steps



@scenario('features/azure_engine.feature', 'Payload logging')
def test_azure_native_payload_logging():
    pass


@given("Azure credentials")
def azure_credentials():
    return {
        "client_id": "29f007c5-4c45-4210-8a88-9a40136f0ddd",
        "client_secret": "e4d8b0fa-73f7-4b77-83a7-0b424d92940f",
        "subscription_id": "744bca72-2299-451c-b682-ed6fb75fb671",
        "tenant": "fcf67057-50c9-4ad4-98f3-ffca64add9e9"
    }


@given("an environment prepared")
def env_prepared(prepare_env):
    pass


@given("set up datamart")
def datamart_setup(ai_client, database_credentials, schema_name):
    print("-- setting up data mart...")
    ai_client.data_mart.setup(db_credentials=database_credentials, schema=schema_name)
    yield
    print("-- removing data mart...")
    ai_client.data_mart.delete()


@given("binding Azure instance")
def binding_uid(ai_client, azure_credentials):
    print("-- binding Azure engine...")
    binding_uid = ai_client.data_mart.bindings.add("Azure ml engine", AzureMachineLearningInstance(azure_credentials))
    yield binding_uid
    print("-- unbinding Azure engine...")
    ai_client.data_mart.bindings.delete(binding_uid)


@given("source id")
def source_id(ai_client):
    asset_details = ai_client.data_mart.bindings.get_asset_details()
    print('Assets details: ' + str(asset_details))

    for detail in asset_details:
        if 'ProductLineAgeRe.2018.10.22.7.33.27.127' in detail['name']:
            return detail['source_uid']


@given("create subscription")
def subscription(ai_client, source_id, binding_uid):
    print("-- creating subscription...")
    subscription = ai_client.data_mart.subscriptions.add(
        AzureMachineLearningAsset(source_uid=source_id,
                                  binding_uid=binding_uid,
                                  input_data_type=InputDataType.STRUCTURED,
                                  problem_type=ProblemType.REGRESSION,
                                  label_column='AGE',
                                  prediction_column='Scored Labels'))
    print("-- subscription id: {}".format(subscription.uid))
    yield subscription
    print("-- removing subscription...")
    ai_client.data_mart.subscriptions.delete(subscription_uid=subscription.uid)


@when("payload logging is enabled")
def enable_payload(ai_client, subscription):
    payload_logging_details = subscription.payload_logging.get_details()
    print('Payload logging details: ' + str(payload_logging_details))


@when("model is scored")
def score_model(ai_client, subscription):
    subscription_details = subscription.get_details()

    scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']

    data = {
        "Inputs": {
            "input1":
                [
                    {
                        'GENDER': "F",
                        'AGE': "27",
                        'MARITAL_STATUS': "Single",
                        'PROFESSION': "Professional",
                        'PRODUCT_LINE': "Personal Accessories",
                    }
                ],
        },
        "GlobalParameters": {
        }
    }

    body = str.encode(json.dumps(data))

    token = subscription_details['entity']['deployments'][0]['scoring_endpoint']['credentials']['token']
    headers = subscription_details['entity']['deployments'][0]['scoring_endpoint']['request_headers']
    headers['Authorization'] = ('Bearer ' + token)

    start_time = time.time()
    response = requests.post(url=scoring_url, data=body, headers=headers)
    response_time = time.time() - start_time
    result = response.json()

    request = {'fields': list(data['Inputs']['input1'][0]),
               'values': [list(x.values()) for x in data['Inputs']['input1']]}

    response = {'fields': list(result['Results']['output1'][0]),
                'values': [list(x.values()) for x in result['Results']['output1']]}

    records_list = [PayloadRecord(request=request, response=response, response_time=int(response_time)),
                    PayloadRecord(request=request, response=response, response_time=int(response_time))]

    subscription.payload_logging.store(records=records_list)
    time.sleep(20)


@then("payload table should exist")
def check_payload_table(ai_client, subscription):
    payload_table_content = subscription.payload_logging.get_table_content(format='python')
    assert 'Scored Labels' in str(payload_table_content)

    subscription.payload_logging.print_table_schema()
    subscription.payload_logging.show_table()
    subscription.payload_logging.describe_table()
    pandas_df = subscription.payload_logging.get_table_content()
    print(str(pandas_df))
    assert pandas_df.size > 1