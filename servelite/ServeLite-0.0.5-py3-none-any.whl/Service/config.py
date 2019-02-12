

from Config import Config, JSONKeeper
from Service.permission import token_check, handel_res


class baseConfig(Config):
    TABLE_IGNORE = ['alembic_version', 'tables', 'fields']
    URI = 'mysql+pymysql://root:0912@127.0.0.1:3306/frame_test?charset=utf8'
    # restless
    PREPROCESSORS = {
        'GET_SINGLE': [token_check],
        'GET_MANY': [token_check]
    }
    POSTPROCESSORS = {
        'GET_SINGLE': [handel_res],
        'GET_MANY': [handel_res]
    }
    # rsa
    PUBKEY_FILE = 'public.pem'
    PRIVKEY_FILE = 'private.pem'
    # service_info
    '''
    service_info存放信息的原则：
        - 需要被持久记录
        - 没有其他文件记录了该信息
    '''
    SERVICE_INFO_FILE = 'service_info.json'
    SERVICE_INFO_ITEMS =[
        'hash',  # 服务hash
        'confirmed', # 确认标志，在服务器首次确认后为确认时间戳
        'reg_url', # 注册中心域名，首次消息推送更新
        'reg_pubkey', # 注册中心pubkey
        'reg_service',
            # get_JWT # JWT更新
            # info_update # info更新
            # api_reg # api注册
            # heartbeat # 心跳包
        'service_call', # 服务调用
            # format: service_endpoint: url
    ]
    SERVICE_INFO = JSONKeeper(SERVICE_INFO_FILE, {i:None for i in SERVICE_INFO_ITEMS})


default = baseConfig()

used_config = default

