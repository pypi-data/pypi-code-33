from .fixtures import *
from pytest_bdd import scenario, given, when, then


@scenario('features/gateway_response_time.feature', 'Get Azure deployments')
def test_azure_native_payload_logging():
    pass


@given('AIOS client instance')
def aios_client_instance(ai_client):
    return ai_client


@given('threshold from Azure get deployments method')
def threashold_azure_deployments():
    pass


@when('get deployments using ML Gateway')
def get_deployments_ml_gateway():
    pass


@then('response time should be less than threshold')
def compare_response_times():
    pass