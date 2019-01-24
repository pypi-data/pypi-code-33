import requests
import re
from json import loads
from .exam import exam
from .man import man
from .utils import getRandomHeader
from .exceptions import *

class Zhixuewang(man, exam):
    def __init__(self, username, password):
        __session = self.__login(username, password)
        self.__session = __session
        __session.headers = {"user-agent": getRandomHeader()}
        if not self.__get_info():
            raise UserDefunctError("帐号已失效")
        man.__init__(self, __session)
        exam.__init__(self, __session)

    def __text_session(self, session):
        r = session.get("http://www.zhixue.com/container/container/student/index/")
        return True if not r.history else False

    @staticmethod
    def _text_password(username, password):
        __session = requests.Session()
        p = {
            "loginName": username,
            "password": password,
            "code": ""
        }
        data = __session.post("http://www.zhixue.com/weakPwdLogin/?from=web_login", data=p).json()
        if data["result"] != "success":
            raise UserOrPassError("用户名或密码错误")
        return __session, data['data']

    def __login(self, username, password):
        __session, userid = self._text_password(username, password)
        msg = __session.get(
            "http://sso.zhixue.com/sso_alpha/login?service=http://www.zhixue.com:80/ssoservice.jsp").text
        data = loads(re.search("{.+}", msg).group())
        p = {
            "username": userid,
            "password": password,
            "sourceappname": "tkyh,tkyh",
            "key": "id",
            "_eventId": "submit",
            "lt": data["lt"],
            "execution": data["execution"],
        }
        msg = __session.get("http://sso.zhixue.com/sso_alpha/login?service=http://www.zhixue.com:80/ssoservice.jsp",
                            params=p).text
        st = re.search('"st": "(.+)"', msg).group(1)
        p = {
            "action": "login",
            "username": userid,
            "password": password,
            "ticket": st,
        }
        __session.post("http://www.zhixue.com:80/ssoservice.jsp", data=p)
        self.id = userid
        return __session

    def __get_info(self):
        r1 = self.__session.get("http://www.zhixue.com/container/container/student/account/", 
                params={"userId": self.id})
        json_data = r1.json()['student']
        try:
            self.name = json_data['name']
            self.school = json_data['clazz']['school']['name']
            self.class_ = json_data['clazz']['name']
        except:
            return False
        return True
