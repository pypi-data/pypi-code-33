import enum
import requests
import time
import datetime
import random


class CheckType(enum.Enum):
    # 前面为方法名，后面为最大等待时间(单位：min)
    CHECK_IN = 'checkin', 11
    CHECK_OUT = 'checkout', 50
    LOGIN_CHECK = '', 0.5


def wait(check_type, delay):
    # 最少要延迟20s
    t = random.randint(20, check_type.value[1] * 60)

    if check_type == CheckType.LOGIN_CHECK or delay:
        print('\n\twill be waiting for ' + str(t) + ' seconds!\n')
        time.sleep(t)
    else:
        print('don\'t sleep')


class AutoChecker:
    __check_headers = {
        'User-Agent': 'E-MobileE-Mobile 6.5.64 (iPhone; iOS 12.1; zh_CN)',
        'Accept-Encoding': 'gzip',
        'Connection': 'keep-alive',
    }

    def __init__(self, config, test, delay):
        self.__udid = config.get_property('udid')
        self.__username = config.get_property('username')
        self.__password = config.get_property('password')
        self.__latlng = config.get_property('latlng')
        self.__addr = config.get_property('addr')
        self.__server = config.get_property('server')
        self.__test = test
        self.__delay = delay

    def __get_cio_cookie(self, user_key='', session_id='', user_id='1'):
        return dict([('ClientCountry', 'CN'), ('ClientLanguage', 'zh-Hans'), ('ClientMobile', ''), ('ClientToken', ''),
                     ('ClientType', 'iPhone'), ('ClientUDID', self.__udid), ('ClientVer', '6.5.64'),
                     ('JSESSIONID', session_id),
                     ('Pad', 'false'), ('setClientOS', 'iOS'), ('setClientOSVer', '12.1'), ('userKey', user_key),
                     ('userid', user_id)])

    def __check_inout(self, check_type):
        url = 'http://' + self.__server + '/client.do?method=checkin&type=' + check_type.value[0] + '&latlng=' + self.__latlng + '&addr=' + self.__addr + '&sessionkey=abcTX_cZ9RjYt5MD_CjBw&wifiMac='

        # 先等待，营造随机效果
        # 如果需要延时
        wait(check_type, self.__delay)
        # 登录获取cookie
        args = self.__login()
        # 登录后等待一段时间
        wait(CheckType.LOGIN_CHECK, self.__delay)

        if not self.__test:
            r = requests.get(url, headers=self.__check_headers, cookies=self.__get_cio_cookie(args['user_key'], args['session_id'], args['user_id']))
            print(self.__username + ' -- ' + str(r.status_code) + ' ---> ' + r.text)
        else:
            print(self.__username + ' *** ' + url)



    # 登录获取最新cookie
    def __login(self):
        headers = {
            'Host': self.__server,
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'Proxy-Connection': 'close',
            'Timezone': 'GMT+8',
            'User-Agent': 'E-MobileE-Mobile 6.5.64 (iPhone; iOS 12.1; zh_CN)',
            'Content-Length': '25',
            'Accept-Encoding': 'gzip',
            'Connection': 'close'
        }
        url = 'http://' + self.__server + '/client.do?method=login&udid=' + self.__udid + '&token=&language=zh-Hans&country=CN&isneedmoulds=1&clienttype=iPhone&clientver=6.5.64&clientos=iOS&clientosver=12.1&authcode=&dynapass=&tokenpass=&clientChannelId=&clientuserid=&relogin=';
        data = {
            'loginid': self.__username,
            'password': self.__password
        }
        r = requests.post(url, data=data, headers=headers, cookies=self.__get_cio_cookie(), timeout=2)
        try:
            cookies = dict([('user_key', r.cookies['userKey']), ('session_id', r.cookies['JSESSIONID']),
                     ('user_id', r.cookies['userid'])])
            print(self.__username + ' -- ' + str(cookies))
            return cookies
        except Exception as e:
            print(self.__username + ' -- 登录失败 --' + r.text)
            raise e
            exit('登录失败')

    # 延时等待
    def check(self):
        # 获取当前时间
        current_time = int((datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%H'))
        # 根据时间进行判断进行签到、签退
        if 8 <= current_time <= 9:
            print('签到({}):'.format(self.__username))
            self.__check_inout(CheckType.CHECK_IN)
        elif 18 <= current_time <= 20:
            print('签退({}):'.format(self.__username))
            self.__check_inout(CheckType.CHECK_OUT)
        elif self.__test:
            print('\n--\tTest({}):\t--\n'.format(self.__username))
            self.__check_inout(CheckType.CHECK_IN)
            self.__check_inout(CheckType.CHECK_OUT)
        else:   
            print('\n\t{}--不在正常时间内，不建议进行签到/退操作。\n'.format(self.__username))
            
