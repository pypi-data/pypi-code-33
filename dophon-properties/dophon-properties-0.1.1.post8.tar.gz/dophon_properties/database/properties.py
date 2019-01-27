# encoding:utf-8
"""
配置相关
"""
import re
from . import default_properties


def init_properties():
    try:
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
        return properties
