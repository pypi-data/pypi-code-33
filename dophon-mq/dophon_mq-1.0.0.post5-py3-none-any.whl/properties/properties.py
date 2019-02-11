"""
配置相关
"""
import sys
import re

try:
    default_properties = __import__('dophon_mq.properties.default_properties', fromlist=True)
    properties = __import__('dophon.properties', fromlist=True)
except:
    try:
        properties = __import__('application', fromlist=True)
    except:
        try:
            properties = __import__('config', fromlist=True)
        except:
            properties = default_properties
finally:
    # 合成配置
    for name in dir(default_properties):
        if not re.match('^__.+__$',name) and not hasattr(properties,name):
            setattr(properties,name,getattr(default_properties,name))
    sys.modules['properties'] = properties
    sys.modules['dophon_mq.properties'] = properties
    sys.modules['dophon_mq.properties.properties'] = properties
    sys.modules['dophon.mq.properties'] = properties
    sys.modules['dophon.mq.properties.properties'] = properties
