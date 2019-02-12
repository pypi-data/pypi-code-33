

from Config import JSONKeeper, Config

class Default(Config):
    URI = 'mysql+pymysql://root:0912@127.0.0.1:3306/reg_test?charset=utf8'
    SECRET_KEY = 'asdeqweqzxcasd'
    # rsa
    PUBKEY_FILE = 'public.pem'
    PRIVKEY_FILE = 'private.pem'
    # service_info
    SERVICE_INFO_FILE = 'service_info.json'
    SERVICE_INFO = JSONKeeper(SERVICE_INFO_FILE)

default = Default()