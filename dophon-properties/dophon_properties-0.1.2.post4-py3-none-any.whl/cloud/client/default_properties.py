# encoding:utf-8
from ..utils import DictObject

# 此处为微服务服务端配置
center_type = 'DOPHON'
cloud_debug_trace = False
client = DictObject({
    'center': ','.join(['http://127.0.0.1:8761/eureka']),
    'host': '127.0.0.1',
    'prefer_ip': False
})
