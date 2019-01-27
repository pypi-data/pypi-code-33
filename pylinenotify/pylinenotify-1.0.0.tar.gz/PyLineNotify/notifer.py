# coding:UTF-8
import os
import requests

class Notifer(object):
    """
    Notifer Object
    :member notify_token:
    """
    def __init__(self,notify_token):
        """
        __init__
        :param notify_token:
        Your LineNotify Acess Token

        """
        self.notify_token=notify_token

    def send_message( self,strings):
        """
        引数に与えられた文字列をLINENotifyで通知する関数
        :param strings:
            通知する文字列
        :return response:
        """
        print ( strings )
        url = 'https://notify-api.line.me/api/notify'
        header = {'Authorization': 'Bearer ' + self.notify_token}
        message = strings
        payload = {'message': message}
        res = requests.post ( url, data=payload, headers=header )
        return str ( res )

def send_message(token,strings):
    """
    引数に与えられた文字列をLINENotifyで通知する関数
    :param strings:
        通知する文字列
    :param token:
        LineNotifyToken
    :return response:
    """
    print ( strings )
    url = 'https://notify-api.line.me/api/notify'
    header = {'Authorization': 'Bearer ' + token}
    message = strings
    payload = {'message': message}
    res = requests.post ( url, data=payload, headers=header )
    return str ( res )


