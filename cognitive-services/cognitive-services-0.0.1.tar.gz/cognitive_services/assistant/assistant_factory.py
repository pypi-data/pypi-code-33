from .assistant_exception import AssistantException
from .watson_assistant import WatsonAssistant


class AssistantFactory:

    @staticmethod
    def create(service_type, credentials):

        if service_type is None:
            raise AssistantException(code=400, message='Missing service_type parameter')

        if service_type.lower() == 'watson':
            return WatsonAssistant(credentials)
        else:
            raise AssistantException(code=400, message=f'Type {service_type} is not supported')
