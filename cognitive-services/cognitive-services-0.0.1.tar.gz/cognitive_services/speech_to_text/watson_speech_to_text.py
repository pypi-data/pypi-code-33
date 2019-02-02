import requests
from watson_developer_cloud import SpeechToTextV1, watson_service
from .speech_to_text import SpeechToText
from .speech_to_text_exception import SpeechToTextException


class WatsonSpeechToText(SpeechToText):

    def __init__(self, credentials):
        username = credentials.get('username')
        password = credentials.get('password')
        errors = []

        if not username:
            errors.append("username")
        if not password:
            errors.append("password")

        if len(errors) > 0:
            raise SpeechToTextException(code=400, message='Missing parameters: {0}'.format(', '.join(errors)))

        self.speechToText = SpeechToTextV1(
            username=username,
            password=password
        )

    def recognize(self, audio, language):
        errors = []

        if not language:
            errors.append("language")
        if not audio:
            errors.append("audio")

        if len(errors) > 0:
            raise SpeechToTextException(code=400, message='Missing parameters: {0}'.format(', '.join(errors)))

        if language == 'en':
            model = 'en-US_BroadbandModel'
        elif language == 'pt-br':
            model = 'pt-BR_NarrowbandModel'
        else:
            raise SpeechToTextException(code=400, message='Invalid language value')

        return self.speechToText.recognize(
            audio=audio,
            model=model
        )

    def recognize_from_url(self, audio_url, language):
        errors = []

        if not language:
            errors.append("language")
        if not audio_url:
            errors.append("audio_url")

        if len(errors) > 0:
            raise SpeechToTextException(code=400, message='Missing parameters: {0}'.format(', '.join(errors)))

        if language == 'en':
            model = 'en-US_BroadbandModel'
        elif language == 'pt-br':
            model = 'pt-BR_NarrowbandModel'
        else:
            raise SpeechToTextException(code=400, message='Invalid language value')

        try:
            r = requests.get(audio_url)

            if r.status_code == 200:
                return self.speechToText.recognize(
                    audio=r.content,
                    model=model
                )
            else:
                raise SpeechToTextException(code=r.status_code, message=f'Problem downloading file {audio_url}')
        except watson_service.WatsonApiException as ex:
            raise SpeechToTextException(code=ex.code, message=ex.message)
        except Exception as ex:
            raise SpeechToTextException(code=500, message=ex.args[0])
