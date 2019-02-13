# coding=utf-8
'''
Created on 2019年2月13日

@author: zy
'''
import unittest
from atc_utils import util

class TestVoice(unittest.TestCase):


    def test_001_is_has_voice(self):
        voice = util.VoiceUtil
        flag = voice.is_has_voice('resources/test_wusheng.wav')
        self.assertFalse(flag, 'wav wusheng file has data')
        flag = voice.is_has_voice('resources/test.wav')
        self.assertTrue(flag, 'wav yousheng file has not data')
        flag = voice.is_has_voice('resources/test_empty.mp4')
        self.assertFalse(flag, 'mp4 wusheng file has data')
        flag = voice.is_has_voice('resources/test.mp4')
        self.assertTrue(flag, 'mp4 yousheng file has not data')
    
    def test_002_asr(self):
        voice = util.VoiceUtil
        result = voice.asr('resources/test.mp4')['result'][0]
        print result
        self.assertIsNotNone(result, 'has word')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()