from .speech_to_text_exception import SpeechToTextException
from .google_speech_to_text import GoogleSpeechToText
from .watson_speech_to_text import WatsonSpeechToText


class SpeechToTextFactory:

    @staticmethod
    def create(service_type, credentials):

        if service_type is None:
            raise SpeechToTextException(code=400, message='Missing service_type parameter')

        if service_type.lower() == 'google':
            return GoogleSpeechToText(credentials)
        elif service_type.lower() == 'watson':
            return WatsonSpeechToText(credentials)
        else:
            raise SpeechToTextException(code=400, message=f'Type {service_type} is not supported')
