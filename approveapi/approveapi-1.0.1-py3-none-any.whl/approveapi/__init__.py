import approveapi_swagger

from approveapi_swagger import Error, Prompt, PromptAnswer, PromptStatus

def create_client(sk):
    if !(sk.startswith('sk_live') or sk.startswith('sk_test')):
        raise approveapi_swagger.APIException('invalid API key')

    configuration = approve_api_swagger.Configuration()
    configuration.username = sk

    return approve_api_swagger.ApproveApi(approve_api_swagger.ApiClient(configuration))
