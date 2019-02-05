import os
import requests
import time


API_KEY = os.environ['TWOCAPTCHA_API_KEY']
ERROR_WRONG_USER_KEY = 'ERROR_WRONG_USER_KEY'
ERROR_KEY_DOES_NOT_EXIST = 'ERROR_KEY_DOES_NOT_EXIST'
ERROR_ZERO_BALANCE = 'ERROR_ZERO_BALANCE'
CAPTCHA_NOT_READY = 'CAPCHA_NOT_READY'


class TwoCaptchaService(object):
    
    def get_recaptcha_v2_answer(self, site_key, url):
        session = requests.Session()
        try:
            captcha_id = session.post(
                "http://2captcha.com/in.php?key={0}&method=userrecaptcha&googlekey={1}&pageurl={2}".format(API_KEY,
                                                                                                           site_key,
                                                                                                           url)).text
            if captcha_id == ERROR_WRONG_USER_KEY or captcha_id == ERROR_KEY_DOES_NOT_EXIST \
                    or captcha_id == ERROR_ZERO_BALANCE:
                return None
            captcha_id = captcha_id.split('|')[1]
            print(captcha_id)
            recaptcha_answer = CAPTCHA_NOT_READY
            while CAPTCHA_NOT_READY in recaptcha_answer:
                try:
                    time.sleep(5)
                    recaptcha_answer = session.get(
                        "http://2captcha.com/res.php?key={0}&action=get&id={1}".format(API_KEY, captcha_id)).text
                except:
                    continue
            return recaptcha_answer.split('|')[1]
        except:
            return None

    def get_captcha_answer(self, captcha_path):
        session = requests.Session()
        try:
            data = {'key': API_KEY}
            files = {'file': open(captcha_path, 'rb')}
            captcha_id = session.post(url='http://2captcha.com/in.php', data=data, files=files).text
            if captcha_id == ERROR_WRONG_USER_KEY or captcha_id == ERROR_KEY_DOES_NOT_EXIST \
                    or captcha_id == ERROR_ZERO_BALANCE:
                return None
            captcha_id = captcha_id.split('|')[1]
            print(captcha_id)
            captcha_answer = CAPTCHA_NOT_READY
            while CAPTCHA_NOT_READY in captcha_answer:
                try:
                    time.sleep(5)
                    params = {'key': API_KEY, 'action': 'get', 'id': captcha_id}
                    captcha_answer = session.get(url='http://2captcha.com/res.php', params=params).text
                except:
                    continue
            if captcha_answer == 'ERROR_CAPTCHA_UNSOLVABLE':
                return captcha_answer
            return captcha_answer.split('|')[1]
        except:
            return None

    def get_captcha_answer_b64(self, captcha_b64):
        session = requests.Session()
        try:
            data = {'key': API_KEY, 'method': 'base64', 'body': captcha_b64}
            captcha_id = session.post(url='http://2captcha.com/in.php', data=data).text
            if captcha_id == ERROR_WRONG_USER_KEY or captcha_id == ERROR_KEY_DOES_NOT_EXIST \
                    or captcha_id == ERROR_ZERO_BALANCE:
                return None
            captcha_id = captcha_id.split('|')[1]
            print(captcha_id)
            captcha_answer = CAPTCHA_NOT_READY
            while CAPTCHA_NOT_READY in captcha_answer:
                try:
                    time.sleep(5)
                    params = {'key': API_KEY, 'action': 'get', 'id': captcha_id}
                    captcha_answer = session.get(url='http://2captcha.com/res.php', params=params).text
                except:
                    continue
            if captcha_answer == 'ERROR_CAPTCHA_UNSOLVABLE':
                return captcha_answer
            return captcha_answer.split('|')[1]
        except:
            return None