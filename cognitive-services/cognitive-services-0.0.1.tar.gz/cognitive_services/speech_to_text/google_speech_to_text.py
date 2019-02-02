import base64
import json
#from googleapiclient.discovery import build
from .speech_to_text import SpeechToText
from .speech_to_text_exception import SpeechToTextException


class GoogleSpeechToText(SpeechToText):

    def __init__(self, credentials):
        api_key = credentials.get('api_key')

        if not api_key:
            raise SpeechToTextException(code=400, message='Missing parameters: api_key')

        #self.speechToText = build('speech', 'v1', developerKey=api_key)

    def recognize(self, audio, language):

        errors = []
        if not language:
            errors.append("language")
        if not audio:
            errors.append("audio")

        if len(errors) > 0:
            raise SpeechToTextException(code=400, message='Missing parameters: {0}'.format(', '.join(errors)))

        if language == 'en':
            language_code = 'en-US'
        elif language == 'pt-br':
            language_code = 'pt-BR'
        else:
            raise SpeechToTextException(code=400, message='Invalid language value')

        body = {
            'audio': {
                'content': base64.b64encode(audio.read()).decode('utf-8')
            },
            'config': {
                'languageCode': language_code
            }
        }

        # try:
        #     return self.speechToText.speech().recognize(
        #         body=body
        #     ).execute()
        # except Exception as ex:
        #     error = json.loads(ex.content).get('error')
        #     if error:
        #         raise SpeechToTextException(code=error['code'], message=error['message'])
        #     else:
        #         raise SpeechToTextException(code=500, message='Unknown error')

    def recognize_from_url(self, audio_url, language):
        pass
