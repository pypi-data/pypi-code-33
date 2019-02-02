# encoding=utf-8

from nbtest.Utils import Undef, UndefCls
from nbtest.assertpyx import AX

import re
from DictObject import DictObject

class _EBase(object):
    """ 大写开头的属性 is 枚举KEY
        小写开头的方法 is 辅助方法
        关键三元素K/V/T: cls.KEY = Utils.typeByDict(VAL, TEXT=TEXT); cls.key2Text(KEY)
        EnumSingletonInstance[Key<k[0].isupper()>] = Val

        __小写驼峰__ is 实例内置方法
        __大写驼峰__ is 类静态内置方法
        _大写驼峰 is 类静态方法、且整个Based继承树内共用

        枚举KEY和枚举VALUE应当在继承树(__WholeInstance)中都唯一
    """
    Undef = Undef

    @classmethod
    def __IsinstanceT__(cls, inst):
        """ Utils.isInstanceT(inst, cls_) == cls_.__IsinstanceT__(inst) """
        return inst in cls.__SingletonInstance.__getVals__()

    __SingletonClsDc = DictObject({'_EBase': Undef})
    __WholeClsDc = DictObject({'_EBase': Undef})      # 类的继承组单例对象
    __SingletonInstance = UndefCls('_EBase._SingletonInstance()')  # 类的单例对象
    __WholeInstance = UndefCls('_EBase._WholeInstance()')  # 类所属继承树基类的单例对象
    @classmethod
    def _SingletonClsDc(cls):
        AX(cls, '').is_equal_to(_EBase)
        return {'_EBase': _EBase} and _EBase.__SingletonClsDc
    @classmethod
    def _WholeClsDc(cls):
        AX(cls, '').is_equal_to(_EBase)
        return {'_EBase': _EBase} and _EBase.__WholeClsDc
    @classmethod
    def _SingletonInstance(cls, val=Undef):
        if val != Undef:
            # print('  {}._SingletonInstance({!r})'.format(cls.__name__, val))
            AX(val, '').is_instance_of(cls)
            AX(cls.__SingletonInstance, '').isIn([Undef, val])
            cls.__SingletonInstance = val
        AX(cls.__SingletonInstance, '').is_not_equal_to(Undef)
        return cls and cls.__SingletonInstance
    @classmethod
    def _WholeInstance(cls, val=Undef):
        if val != Undef:
            # print('  {}._WholeInstance({!r})'.format(cls.__name__, val))
            AX(val, '').is_instance_of(cls)
            AX(cls.__WholeInstance, '').isIn([Undef, val])
            cls.__WholeInstance = val
        AX(cls.__WholeInstance, '').is_not_equal_to(Undef)
        return cls and cls.__WholeInstance

    class _ValObj(object):
        def __init__(self, VAL):
            bases = self.__class__.__bases__
            note = '{!r}.__bases__'.format(self.__class__)
            AX(bases, note).is_length(2)
            AX(bases, note).doGeti(0).is_equal_to(_EBase._ValObj)
            bases[1].__init__(self, VAL)  # #调用未绑定的超类构造方法【必须显式调用父类的构造方法】
            self.VAL = VAL      # VAL用于接口层次
            self.TEXT = Undef   # TEXT用于UI层次

        def __DefAttrs__(self, TEXT, **kw):
            AX(TEXT, 'TEXT').is_instance_of(basestring)
            self.TEXT = TEXT
            for k, v in kw.items():
                assert k[:1].isupper() and (k not in ['VAL', 'TEXT']), \
                    "assert k[0].isupper() and (k not in ['VAL', 'TEXT']), but k={!r}".format(k)
                setattr(self, k, v)
            return self

        @classmethod
        def defVal(cls, VAL, TEXT=Undef, **kw):
            return cls(VAL).__DefAttrs__(TEXT, **kw)
        def __getitem__(self, item):
            return getattr(self, item)

    @classmethod
    def defVal(cls, VAL, TEXT=Undef, **kw):
        return cls._ValObj(VAL).__DefAttrs__(TEXT, **kw)

    def __init__(self, **kw):
        cls = self.__class__
        AX(cls.__name__, 'cls.__name__').is_not_in(*_EBase._SingletonClsDc().keys())
        _EBase._SingletonClsDc()[cls.__name__] = cls
        self.__class__.__SingletonInstance = self
        self.__objName__ = self.__class__.__name__

    @classmethod
    def __Singleton__(cls, **kw):
        return cls(**kw)

    @classmethod
    def __CreateWholeClsThenSingleton__(cls, name='EQueuesLiked', chkMethod=None):
        AX(cls, 'cls').is_equal_to(_EBase)
        AX(name, 'name').is_instance_of(basestring)
        bases = [_v for _k, _v in _EBase._SingletonClsDc().items() \
                   if _k.startswith('{}_'.format(name)) and not re.match(r'_[a-z0-9_]', _k)]
        wholeCls = _EBase and type(
            name,
            tuple(bases),
            {}
        )
        AX(name, 'name').is_not_in(*_EBase._WholeClsDc().keys())
        _EBase._WholeClsDc()[name] = wholeCls
        wholeInstance = wholeCls.__Singleton__(isWholeInstance=True)
        for base in bases:
            if chkMethod:
                getattr(base, chkMethod)()
            base._WholeInstance(wholeInstance)
        wholeCls._WholeInstance(wholeInstance)
        return wholeInstance

    def __getitem__(self, item):
        """ inst.KEY === inst[KEY] """
        return getattr(self, item)

    def __getItems__(self):
        items = {k: (self.__class__._ValObj and self[k]) for k in dir(self) if k[0].isupper()}
        items.pop('Undef')
        return items

    def __getKeys__(self):
        return self.__getItems__().keys()

    def __getVals__(self):
        return sorted(self.__getItems__().values())

    def __doUndef__(self, name):
        return UndefCls('{}.{}'.format(self.__objName__, name))

    def __doDefault__(self, method, srcKey, **kw):
        if not kw.has_key('__Dft__'):
            assert False, self.__doUndef__('{}({!r})'.format(method, srcKey))
        else:
            return kw['__Dft__']

    def __chkVal__(self, enumVal):
        AX(enumVal, '%s:enumVal' % self.__objName__).isIn(self.__getVals__())

    def key2Val(self, enumKey, **kw):
        srcDict = self.__getItems__()
        if not srcDict.has_key(enumKey):
            ret = self.__doDefault__('key2Val', enumKey, **kw)
        else:
            ret = srcDict[enumKey]
        return self.__class__._ValObj and ret

    def val2Obj(self, enumVal, **kw):
        enumKey = self.val2Key(enumVal, **kw)
        return self.key2Val(enumKey, **kw)

    def getValSon(self, val, son='TEXT', **kw):
        valObj = self.val2Obj(val, **kw)
        if isinstance(valObj, _EBase._ValObj):  # 注意这里要用_EBase._ValObj，确保是valObj形式而不是原始的val形式
            return valObj[son]
        else:
            return kw['__Dft__']

    def getValSons(self, son='TEXT'):
        return [v[son] for v in self.__getVals__()]

    def key2Text(self, enumKey, **kw):
        val = self.key2Val(enumKey, **kw)
        return self.getValSon(val, 'TEXT')

    def val2Text(self, enumVal, **kw):
        enumKey = self.val2Key(enumVal, **kw)
        return self.key2Text(enumKey, **kw)

    def val2Key(self, enumVal, **kw):
        for k, v in self.__getItems__().items():
            if v == enumVal:
                return k
        else:
            return self.__doDefault__('val2Key', enumVal, **kw)

    def __chkWholeInstance__(self):
        AX(self, 'self').is_equal_to(self.__class__._WholeInstance())

    def __chkSingletonInstance(self):
        AX(self, 'self').is_equal_to(self.__class__._SingletonClsDc())
        AX(self, 'self').is_not_equal_to(self.__class__._WholeInstance())

    def __wholeVal2SingletonInstance__(self, enumVal, **kw):
        cls = self.__class__
        self.__chkWholeInstance__()
        wholeCls = _EBase._WholeClsDc()[cls._SingletonInstance().__objName__]
        for base in wholeCls.__bases__:
            instance = (_EBase and base)._SingletonInstance()
            if enumVal in instance.__getVals__():
                return instance
        else:
            assert False, "cann't find enumVal={!r} in cls={}".format(enumVal, cls.__name__)



