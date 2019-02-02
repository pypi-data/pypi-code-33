import websocket
import json
from threading import Thread
from watson_developer_cloud import AuthorizationV1
from .speech_to_text_web_socket import SpeechToTextWebSocket


class WatsonSpeechToTextWebSocket(SpeechToTextWebSocket):

    __URI__ = 'wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize'

    def __init__(self, consumer, credentials, language, frame_rate):
        Thread.__init__(self)
        SpeechToTextWebSocket.__init__(self, consumer, credentials, language, frame_rate)

    def run(self):
        print("Starting thread")

        auth = AuthorizationV1(username='b0398c98-75e8-4628-ac72-58722de24946',
                               password='5UAUkSXZhNuv')

        token = auth.get_token('https://stream.watsonplatform.net/speech-to-text/api')

        url = '{0}?watson-token={1}&model={2}'.format(self.__URI__, token, 'pt-BR_NarrowbandModel')

        self.ws = websocket.WebSocketApp(url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.keep_running = True
        self.ws.daemon = True
        self.ws.run_forever()

    def start_client(self):
        message = {
            'action': 'start',
            'content-type': 'audio/wav'
        };
        self.ws.send(json.dumps(message), websocket.ABNF.OPCODE_TEXT)
        self.ws.send(SpeechToTextWebSocket.get_wave_header(self.nchannels, self.sample_width, self.frame_rate),
                     opcode=websocket.ABNF.OPCODE_BINARY)
        if self.bytes:
            self.send_data(self.bytes)

    def send_data(self, data):
        if not self.is_open:
            self.bytes += data
        elif self.bytes:
            self.ws.send(self.bytes, opcode=websocket.ABNF.OPCODE_BINARY)
            self.bytes = b''
        else:
            self.ws.send(data, opcode=websocket.ABNF.OPCODE_BINARY)

    def close_client(self):
        message = {
            'action': 'stop'
        }
        self.ws.send(json.dumps(message), websocket.ABNF.OPCODE_TEXT)

    def stop(self):
        print('stopping')
        self.ws.keep_running = False

