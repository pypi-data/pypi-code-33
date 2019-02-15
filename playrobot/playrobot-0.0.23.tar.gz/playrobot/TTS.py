from gtts import gTTS
from gtts_token.gtts_token import Token
from pygame import mixer
import calendar
import time
import math
import re
import requests

#語音輸出
def _patch_faulty_function(self):
    if self.token_key is not None:
        return self.token_key

    timestamp = calendar.timegm(time.gmtime())
    hours = int(math.floor(timestamp / 3600))

    results = requests.get("https://translate.google.com/")
    tkk_expr = re.search("(tkk:*?'\d{2,}.\d{3,}')", results.text).group(1)
    tkk = re.search("(\d{5,}.\d{6,})", tkk_expr).group(1)
    
    a , b = tkk.split('.')

    result = str(hours) + "." + str(int(a) + int(b))
    self.token_key = result
    return result

Token._get_token_key = _patch_faulty_function

def wordToSound(text):
    file_name ='test2.mp3'
    tts = gTTS(text, lang='zh-tw')
    tts.save(file_name)
    mixer.init()
    mixer.music.load(file_name)
    mixer.music.play()
    while mixer.music.get_busy() == True:
        continue
    mixer.music.stop()
    mixer.quit()
