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
            elif not re.match('^__.+__$',name):
                from ..utils import DictObject
                # 特别配置
                def_dict_obj = getattr(default_properties,name)
                if isinstance(def_dict_obj,DictObject):
                    # print(f'{name} - {def_dict_obj}')
                    custom_dict = getattr(properties, name)
                    for k,v in custom_dict.items():
                        def_dict_obj[k] = v
                    setattr(properties,name,def_dict_obj)
        return properties
