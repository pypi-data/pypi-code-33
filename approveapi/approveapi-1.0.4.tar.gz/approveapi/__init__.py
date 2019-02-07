import approveapi_swagger

from approveapi_swagger import Error, Prompt, PromptAnswer, PromptStatus
from approveapi_swagger.rest import APIException

def create_client(sk):
    if not(sk.startswith('sk_live') or sk.startswith('sk_test')):
        raise APIException('invalid API key')

    configuration = approveapi_swagger.Configuration()
    configuration.username = sk

    return approveapi_swagger.ApproveApi(approveapi_swagger.ApiClient(configuration))


