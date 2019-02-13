#coding=utf-8
'''
Created on 2018年11月3日

@author: zy
'''

from aip import AipOcr
from aip import AipSpeech
import tempfile
import os
import subprocess
import wave
import numpy as np

def exec_cmd(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

class BaiduOCR(object):
    
    APP_ID = '14661636'
    API_KEY = 'B2oQpcwPTzvBdeK3FXseGT1l'
    SECRET_KEY = 'mPbs4t5SP3itm9cupIjuDglbU9iApP68'
    
    def __init__(self):
        self.client = AipOcr(BaiduOCR.APP_ID, BaiduOCR.API_KEY, BaiduOCR.SECRET_KEY)

    def basicGeneralLocal(self, file_path, options={}):
        '''通用'''
        options["language_type"] = "CHN_ENG"
        options["detect_direction"] = "true"
        options["detect_language"] = "false"
        options["probability"] = "true"
        return self.client.basicGeneral(get_file_content(file_path), options)
    
    def basicAccurate(self,file_path, options={}):
        '''通用高精度'''
        options["langua ge_type"] = "CHN_ENG"
        options["detect_direction"] = "true"
        options["detect_language"] = "false"
        options["probability"] = "true"
        return self.client.basicAccurate(get_file_content(file_path), options)
    
    def enhancedGeneral(self, file_path, options={}):
        '''生僻字'''
        options["langua ge_type"] = "CHN_ENG"
        options["detect_direction"] = "true"
        options["detect_language"] = "false"
        options["probability"] = "true"
        return self.client.enhancedGeneral(get_file_content(file_path), options)

class BaiduVoice(object):
    
    APP_ID = '15520133'
    API_KEY = '1lCVC1uKrE5Aoy71kF0XsF2y'
    SECRET_KEY = '6WYfXKnF4GmkKW5f9TOQjsZ94MoUTRnP'
    
    def __init__(self, ffmpeg=None):
        self.client = AipSpeech(BaiduVoice.APP_ID, BaiduVoice.API_KEY, BaiduVoice.SECRET_KEY)
        self.ffmpge = "ffmpeg.exe" if os.name == 'nt' else "ffmpeg"
    
    def asr(self, speech, format='pcm', rate=16000, options=None):
        result =  self.client.asr(get_file_content(speech), format, rate, options)
        return result
    
    def asr_by_audio(self, wav_path):
        if not self.is_has_voice(wav_path):
            return 
        pcm_path = self.wav2pcm(wav_path)
        result = self.asr(pcm_path)
        os.remove(wav_path)
        os.remove(pcm_path)
        return result
    
    def asr_by_video(self, video_path):
        wav_path = self.extract_audio_by_video(os.path.abspath(video_path))
        if not self.is_has_voice(wav_path):
            return 
        pcm_path = self.wav2pcm(wav_path)
        result = self.asr(pcm_path)
        os.remove(wav_path)
        os.remove(pcm_path)
        return result
    
    def extract_audio_by_video(self, video_path): # 格式 ffmpeg.exe -i test.mp4 -f wav -vn -y 3.wav
        audio = tempfile.mktemp(".wav",'video2wav')
        cmd = "%s -i %s -f wav -vn -y %s"%(self.ffmpge, video_path, audio)
        exec_cmd(cmd).wait()
        return audio
    
    def is_has_voice(self, path, threshold=10000):
        wav_file = wave.open(path, 'rb')
        params = wav_file.getparams()
#         print params
        framesdeep,frames= params[1], params[3]
        data = wav_file.readframes(frames)
        wav_file.close()
        data = np.fromstring(data,dtype = np.short)
        data.shape = -1, framesdeep
        filter_data = np.where(data>threshold,1,0)
        if filter_data.sum(axis=0)[0]> 1000:
            return True
        return False
    
    def wav2pcm(self, wav_path): # 格式ffmpeg -y  -i test.wav  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 test.pcm
        pcm_path = tempfile.mktemp(".pcm",'wav2pcm')
        cmd = "%s -y  -i %s -acodec pcm_s16le -f s16le -ac 1 -ar 16000 %s"%(self.ffmpge, wav_path, pcm_path)
        exec_cmd(cmd).wait()
        return pcm_path

if __name__ == '__main__':
    voice = BaiduVoice()
    print voice.asr_by_video(os.path.abspath('../../test/resources/test.mp4'))['result'][0]
    