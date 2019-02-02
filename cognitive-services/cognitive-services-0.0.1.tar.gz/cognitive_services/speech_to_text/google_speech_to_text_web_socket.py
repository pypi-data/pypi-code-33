import json
import wave
from io import BytesIO

from .google_speech_to_text import GoogleSpeechToText
from .speech_to_text_web_socket import SpeechToTextWebSocket
from .speech_to_text_exception import SpeechToTextException


class GoogleSpeechToTextWebSocket(SpeechToTextWebSocket):

    def __init__(self, consumer, credentials, language, frame_rate):
        SpeechToTextWebSocket.__init__(self, consumer, credentials, language, frame_rate)
        self.mem_audio = None
        self.wave = None

    def run(self):
        print("Starting thread")

        self.mem_audio = BytesIO()
        self.wave = wave.open(self.mem_audio, 'wb')
        self.wave.setnchannels(1)
        self.wave.setsampwidth(2)
        self.wave.setframerate(self.frame_rate)

    def start_client(self):
        pass

    def send_data(self, data):
        self.wave.writeframes(data)

    def close_client(self):
        self.wave.close()
        self.mem_audio.seek(0)

        try:
            print('sending audio to speech to text service')
            speech_to_text = GoogleSpeechToText(self.credentials)
            response = speech_to_text.recognize(
                audio=self.mem_audio,
                language=self.language
            )

            if 'results' in response and len(response['results']) > 0 and \
                    'alternatives' in response['results'][0] and len(response['results'][0]['alternatives']) > 0 and \
                    'transcript' in response['results'][0]['alternatives'][0]:
                self.consumer.send(json.dumps(response['results'][0]['alternatives'][0]))
            else:
                self.consumer.send(json.dumps({'error': 'Não foi possível reconhecer o audio enviado. Tente novamente.'}))

        except SpeechToTextException as ex:
            response = {
                'error': ex.message
            }
        except Exception as ex:
            response = {
                'error': ex.args[0]
            }
        self.consumer.send(json.dumps(response))
