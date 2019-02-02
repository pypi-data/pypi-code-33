import struct
import json
from io import BytesIO
from abc import ABC, abstractmethod
from threading import Thread


class SpeechToTextWebSocket(ABC, Thread):
    @abstractmethod
    def __init__(self, consumer, credentials, language, frame_rate):
        Thread.__init__(self)
        self.ws = None
        self.is_open = False
        self.consumer = consumer
        self.credentials = credentials
        self.language = language
        self.frame_rate = frame_rate
        self.nchannels = 1
        self.sample_width = 2
        self.bytes = b''

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def start_client(self):
        pass

    @abstractmethod
    def send_data(self, data):
        pass

    @abstractmethod
    def close_client(self):
        pass

    def on_message(self, ws, message):

        message_json = json.loads(message)

        if 'results' in message_json:
            if len(message_json['results']) > 0 and \
                'alternatives' in message_json['results'][0] and len(message_json['results'][0]['alternatives']) > 0 \
                    and 'transcript' in message_json['results'][0]['alternatives'][0]:
                self.consumer.send((json.dumps(message_json['results'][0]['alternatives'][0])))
            else:
                self.consumer.send(json.dumps({'error': 'Não foi possível reconhecer o audio enviado. Tente novamente.'}))
        else:
            self.consumer.send(message)

    def on_error(self, ws, error):
        print(error)
        self.consumer.send(json.dumps({'error': error}))

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws):
        print('on_open')
        self.start_client()
        self.is_open = True

    @staticmethod
    def get_wave_header(nchannels, sample_width, frame_rate):

        output = BytesIO()
        output.write(struct.pack('>L', 0x52494646))
        output.write(struct.pack('<L', 0))
        output.write(struct.pack('>L', 0x57415645))
        output.write(struct.pack('>L', 0x666d7420))
        output.write(struct.pack('<L', 16))
        output.write(struct.pack('<H', 0x0001))
        output.write(struct.pack('<H', nchannels))
        output.write(struct.pack('<L', frame_rate))
        output.write(struct.pack('<L', frame_rate * nchannels * sample_width))
        output.write(struct.pack('<H', nchannels * sample_width))
        output.write(struct.pack('<H', sample_width * 8))
        output.write(struct.pack('>L', 0x64617461))
        output.write(struct.pack('<L', 0))

        data = output.getvalue()

        output.close()

        return data

