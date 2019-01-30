import hashlib
import hmac
import time
import random
import os

class MessageAuthentication(object):
    def __init__(self):
        self.api_key = os.getenv('APIKEY')
        if self.api_key == '' or self.api_key is None:
            raise 'API Key is required but has not been defined, please set the APIKEY environment variable to continue.'
        return

    def compute(self, iv, data, debug = False):
        epoch = int(time.time())
        nonce = ''.join([str(random.randint(0, 9)) for i in range(16)])
        secret = bytes(self.api_key, 'utf-8')
        h = hashlib.md5()
        h.update(str(data).encode('utf-8'))
        hash_value = h.hexdigest()

        message = '{}{}{}{}'.format(iv, epoch, nonce, hash_value).encode('utf-8')
        hashmac = hmac.new(secret, message, hashlib.sha256)
        hmac_value = hashmac.hexdigest()
        code = '{}:{}:{}'.format(hmac_value, nonce, epoch)

        if debug:
            self.debug_output(epoch, nonce, secret, hash_value, message, hmac_value)

        return code

    def debug_output(self, epoch, nonce, secret, hash_value, message, message_value):
        print('Epoch: {}'.format(epoch))
        print('Nonce: {}'.format(nonce))
        print('Secret: {}'.format(secret))
        print('Hash: {}'.format(hash_value))
        print('Message: {}'.format(message))
        print('HMAC: {}'.format(message_value))
