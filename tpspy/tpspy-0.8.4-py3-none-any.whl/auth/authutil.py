# -*- coding: utf-8 -*-

import time
import base64
import hashlib
import traceback
import random


class AuthUtil(object):
    def __init__(self):
        self.secret = None

    def set_secret(self, secret):
        self.secret = secret

    def gen_token(self, user_id, expire_sec=3600*24*7):
        expire_stamp = str(int(time.time()) + expire_sec)
        rand = random.randint(10000000, 99999999)
        v = "%s||%s%8d%s" % (user_id, expire_stamp, rand, self.secret)
        md5_value = hashlib.md5(v.encode('utf-8')).hexdigest()
        # print "stamp: %s, rand: %s, md5_value: %s" % (stamp, rand, md5_value)
        raw = "%s||%s%8d%s" % (user_id, expire_stamp, rand, md5_value)
        return base64.b64encode(raw.encode('utf-8')).decode('utf-8')

    def check_token(self, token):
        if not self.secret:
            raise ValueError("AuthUtil MUST set_secret()")

        if not token:
            return False, "invalid token"

        try:
            raw = base64.b64decode(token)
            parts = raw.decode('utf-8').split("||")
            if len(parts) != 2:
                return False, ""
            token_user_name = parts[0]
            body = parts[1]
            if len(body) < 18:
                return False, ""
            expire_stamp = int(body[0:10])
            if int(time.time()) > expire_stamp:
                return False, ""
            md5_value = body[18:]
            v = "%s||%s%s" % (token_user_name, body[0:18], self.secret)
            desire_md5_value = hashlib.md5(v.encode('utf8')).hexdigest()
            # print "stamp: %s, rand: %s, md5_value: %s, desire_md5_value: %s" % (stamp, raw[10:18], md5_value, desire_md5_value)
            if md5_value == desire_md5_value:
                return True, token_user_name
            else:
                return False, "invalid token"
        except:
            traceback.print_exc()
            return False, "unknown error"
