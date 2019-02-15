from aip import AipSpeech
import pyaudio
import wave
from pygame import mixer

APP_ID = ''
API_KEY = ''
SECRET_KEY = ''
client = ''
CHUNK = 1024
RATE = 16000
RECORD_SECONDS = 5


def setProperty(ID = '',AK = '', SK = '',chunk = 1024 ,rate = 16000,rec = 5):
    global APP_ID,API_KEY,SECRET_KEY,client,CHUNK,RATE,RECORD_SECONDS,client
    APP_ID = ID
    API_KEY = AK
    SECRET_KEY = SK
    CHUNK = chunk
    RATE = rate
    RECORD_SECONDS = rec
    client = AipSpeech(APP_ID,API_KEY,SECRET_KEY)

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()
    
def recordWave():
    global CHUNK,RATE,RECORD_SECONDS
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    pa = pyaudio.PyAudio()
    stream = pa.open(format=FORMAT,
                     channels=CHANNELS,
                     rate=RATE,
                     input=True,
                     frames_per_buffer=CHUNK)
    print('Recording...')
    buffer = []
    for i in range(0, int(RATE/CHUNK*RECORD_SECONDS)):
        audio_data = stream.read(CHUNK)
        buffer.append(audio_data)
    print('Record Done')
    stream.stop_stream()
    stream.close()
    pa.terminate()
    wf = wave.open('record.wav', 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pa.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(buffer))
    wf.close()

def STT():
    global APP_ID,API_KEY,SECRET_KEY,client
    if APP_ID == '' or API_KEY == '' or SECRET_KEY == '':
        raise BaseException('please using setProperty to set API Property')
    recordWave()
    result = str(client.asr(get_file_content('record.wav'), 'wav', 16000, {'dev_pid': 1536,})['result'])
    result = result[2:len(result)-2]
    return result

def TTS(target,sound = 1):
    if type(target) != str:
        raise BaseException('input not a string')
    result  = client.synthesis(target, 'zh', sound, {'vol': 5,'spd': 3,})
    if not isinstance(result, dict):
        with open('test.mp3', 'wb') as f:
            f.write(result)
    mixer.init()
    mixer.music.load('test.mp3')
    mixer.music.play()
    while mixer.music.get_busy() == True:
        continue
    mixer.music.stop()
    mixer.quit()
