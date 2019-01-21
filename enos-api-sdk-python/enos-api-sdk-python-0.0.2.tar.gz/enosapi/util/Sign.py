# coding: utf8
# Author:xuyang.li
# EOS API Sign
import logging
from hashlib import sha1


class Sign(object):
    __logging = logging.getLogger(__name__)
    # concat string
    @classmethod
    def make_string(cls, appkey, app_secret, params, body_content=None):
        # check parameter
        assert appkey is not None
        assert app_secret is not None

        sign_str = appkey
        if params is not None:
            keys = sorted(params.keys())
            for key in keys:
                sign_str += key+str(params[key])

        if body_content is not None:
            sign_str += body_content
        sign_str += app_secret
        cls.__logging.info(sign_str)
        return sign_str

    @classmethod
    def sign(cls, appkey, app_secret, params, body_content=None):
        string = Sign.make_string(appkey, app_secret, params, body_content)
        psw = sha1()
        psw.update(string.encode('utf8'))

        return psw.hexdigest().upper()








