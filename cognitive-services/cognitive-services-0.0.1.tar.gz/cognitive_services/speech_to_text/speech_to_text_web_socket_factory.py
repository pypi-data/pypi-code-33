from .speech_to_text_exception import SpeechToTextException
from .google_speech_to_text_web_socket import GoogleSpeechToTextWebSocket
from .watson_speech_to_text_web_socket import WatsonSpeechToTextWebSocket


class SpeechToTextWebSocketFactory:

    @staticmethod
    def create(service_type, credentials):

        if service_type is None:
            raise SpeechToTextException(code=400, message='Missing service_type parameter')

        if service_type.lower() == 'google':
            return GoogleSpeechToTextWebSocket(credentials)
        elif service_type.lower() == 'watson':
            return WatsonSpeechToTextWebSocket(credentials)
        else:
            raise SpeechToTextException(code=400, message=f'Type {service_type} is not supported')
