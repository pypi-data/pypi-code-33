import approveapi_swagger

from approveapi_swagger import Error, Prompt, PromptAnswer, PromptStatus, PromptMetadata, AnswerMetadata, CreatePromptRequest
from approveapi_swagger.rest import ApiException

def create_client(sk):
    if not(sk.startswith('sk_live') or sk.startswith('sk_test')):
        raise ApiException('invalid API key')

    configuration = approveapi_swagger.Configuration()
    configuration.username = sk

    return approveapi_swagger.ApproveApi(approveapi_swagger.ApiClient(configuration))
