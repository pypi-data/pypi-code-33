"""
角色权限控制类, 用于表达某一角色所拥有的权限选项.
这些选项将在前端登录时被返回, 供前端渲染菜单使用.

注意:
这些类应当被设计为可以用于任何权限选项的控制, 而不是单纯针对单一应用的列表渲染.
这些类会在其他模块的权限控制中直接使用.(或者权限管理服务器)
"""
import abc
import json
from typing import List

class Option(metaclass=abc.ABCMeta):
    """
    option抽象类
    """
    @classmethod
    def to_json(cls):
        """
        生成的json需要用前后大括号的方式组织 以统一其他模块的设计
        :return:
        """
        pass

class baseOptions:
    def __init__(self, p_name, p_code, options: list=None):
        """
        :param p_name: 权限名
        :param p_code: 权限id
        :param options: 权限选项
        """
        self.name = p_name
        self.code = p_code
        self.options = options if options else []

    def json_options(self, indent=None):
        """
        返回json格式的options信息
        :return:
        """
        return json.dumps([opt.to_json for opt in self.options], indent=indent, ensure_ascii=False)

    def to_json(self, indent=None):
        """
        json化权限信息用于储存
        :return:
        """
        s = {}
        for i in self.__dir__():
            if not hasattr(self.__getattribute__(i), '__call__') and i[0] != '_' and i[-1] != '_':
                s[i] = self.__getattribute__(i)
        s['options'] = [opt.opt_dict() for opt in self.options]
        return json.dumps(s, indent=indent, ensure_ascii=False)
#------------------------------------------
#  用于边侧栏导航的核心数据服务器options
#------------------------------------------
class SideBarOption(Option):
    def __init__(self, title, key, sub=None):
        self.title = title
        self.key = key
        self.sub = None if sub is None else SideBarOptions(option_list=sub)
        # if sub and self.sub.max_layer == 2: # 最大允许两级选项
        #     raise ValueError('too many layers of sub option')

    def opt_dict(self):
        return {
            'title': self.title,
            'key': self.key,
            'sub': None if self.sub is None else [opt.opt_dict() for opt in self.sub.options]
        }

    def to_json(self, indent=None):
        return json.dumps(self.opt_dict(), indent=indent, ensure_ascii=False)


class SideBarOptions(baseOptions):
    """
    用来表示不同角色可以使用的功能菜单的数据结构。使用一个列表传入初始化数据。
    数据格式：
    [
        {
            'key': opt_key,
            'title': opt_title,
            'sub': [list like this]
        }
    ]
    注意不同角色必须保证每个选项的key是不同的，当某个角色需要在其他角色的选项中添加新选项时，
    会直接使用key搜索option对象

    TODO: 选项排列优先级
    """
    def __init__(self, p_name=None, p_code: int=None, option_list: list = None, max_layer=2):
        self.options = [] # type: List(SideBarOption)
        option_list = option_list if option_list else []
        for i in option_list:
            self.options.append(SideBarOption(i.get('title'), i.get('key'), i.get('sub')))
        super().__init__(p_name, p_code, self.options)
        self.max_layer = max_layer
        # 检查layer
        for i in self.options:
            self.layer_check_(i, 1)

    def layer_check_(self, opt: SideBarOption, layer):
        if opt.sub:
            if layer == self.max_layer:
                raise ValueError('too many layers of sub option. max: {}'.format(self.max_layer))
            for i in opt.sub.options:
                self.layer_check_(i, layer + 1)





