from hashlib import sha1


class SignUtil(object):

    hmacsha1 = 'hmacsha1'

    @classmethod
    def make_string(cls, app_secret, params):

        assert app_secret is not None
        assert params is not None

        keys = sorted(params.keys())
        sign_str = ''
        for key in keys:
            sign_str += key+str(params[key])

        sign_str += app_secret

        return sign_str

    @classmethod
    def sign(cls, app_secret, params):
        string = SignUtil.make_string(app_secret, params)
        psw = sha1()
        psw.update(string.encode('utf8'))

        return psw.hexdigest().upper()



if __name__ == '__main__':
    dict = dict()
    dict['clientId'] = 'NZkdWQLjd0'
    dict['deviceKey'] = 'NZkdWQLjd0'
    dict['productKey'] = '5IpMOFdM'
    dict['timestamp'] = '1543228214879'
    sign = SignUtil.sign('whXTB7IM50M7kBFfta1l', dict)
    # print sign