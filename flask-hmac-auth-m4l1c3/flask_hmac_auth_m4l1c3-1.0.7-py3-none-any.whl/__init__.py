import hashlib
import hmac
import base64
import time
import random
import os
from flask import request
from functools import wraps

nonces = []

def authenticate_request(request):
    if request.environ['HTTP_AUTHORIZATION'] is not None:
        parts = request.environ['HTTP_AUTHORIZATION'].split(":")
        secret = bytes(os.getenv('APIKEY'), 'utf-8')
        max_time = 20

        if len(parts) == 3:
            epoch = int(time.time())
            nonce = parts[1]
            incoming_time = parts[2]
            if epoch - int(incoming_time) < max_time and nonce not in nonces:
                nonces.append(nonce)
                m = hashlib.md5()
                m.update(request.data)
                message = '{}{}{}{}'.format(request.base_url, incoming_time, nonce, m.hexdigest()).encode('utf-8')
                try:
                    hash = hmac.new(secret, bytes(message), hashlib.sha256)
                    t = '{}:{}:{}'.format(hash.hexdigest(), nonce, incoming_time)
                    if request.environ['HTTP_AUTHORIZATION'] == t:
                        return True
                    return False
                except Exception as e:
                    return False
            return False
        return False
    return False

def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not authenticate_request(request):
            return {'Status': 401, 'Message': 'Unauthorized'}
        return f(*args, **kwargs)
    return wrapper
