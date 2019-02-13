# coding=utf-8
'''
Created on 2019年2月13日

@author: zy
'''
from atc_utils.core.baidu import BaiduVoice as Voice
import os

class VoiceUtil(object):
    '''声音相关处理'''
    
    @classmethod
    def is_has_voice(cls, path, threshold=100): # 处理wav，mp4
        voice = Voice()
        extend_name = os.path.splitext(path)[1]
        if '.wav' == extend_name:
            return voice.is_has_voice(path, threshold)
        elif '.mp4' == extend_name:
            wav_path = voice.extract_audio_by_video(path)
            return voice.is_has_voice(wav_path, threshold)
    
    @classmethod
    def asr(cls, path): # 声音转化为文字
        voice = Voice()
        extend_name = os.path.splitext(path)[1]
        if '.wav' == extend_name:
            return voice.asr_by_video(path)
        elif '.mp4' == extend_name:
            return voice.asr_by_video(path)
            
       
        