# encoding=utf-8

import types, numbers, inspect, traceback, time, chardet, re, os, json
import subprocess
from datetime import datetime, timedelta
from DictObject import DictObject
import jsonpath_rw_ext as jpath  # pip install jsonpath_rw_ext

from .future2to3 import *
from .assertpyx import AX, _Utils

_SingletonCls_Stores = {}
def SingletonCls(cls):
    inst = cls.__Singleton__() if hasattr(cls, '__Singleton__') else cls()
    assert cls.__name__ not in _SingletonCls_Stores.keys(),\
        "assert <cls.__name__={!r}> not in <_SingletonCls_Stores.keys()>".format(cls.__name__)
    _SingletonCls_Stores[cls.__name__] = cls
    inst.__SingletonName__ = cls.__name__
    inst.__call__ = lambda: inst
    return inst

def SingletonClsGet(clsName):
    return _SingletonCls_Stores[clsName]

class JsonLike(object):
    def toJson(self, __PathPre__='', **kwargs):
        jsoned = DictObject()
        for i in ObjGet.attrs(self, regMatch='^[a-zA-Z]', limit_callable=False):
            ipath = __PathPre__ + i
            v = getattr(self, i)
            isJsonItem(v, raiseName=self.__class__.__name__ + '::' + ipath)
            jsoned[i] = v if not isinstance(v, JsonLike) else v.toJson(__PathPre__=ipath+'.')
        return jsoned

def isJsonItem(o, raiseName=''):
    if isinstance(o, str):
        o_codetype = encode_get(o)
        if o_codetype not in ['utf-8', 'unicode', 'ascii']:
            raise Exception("need encode_get(o={}) in ['utf-8', 'unicode', 'ascii'], but isa {}, o={!r}"
                            .format(raiseName, o_codetype, o))
    canJsonTypes = (types.NoneType, bool, numbers.Real, basestring, list, dict, JsonLike)
    chk = isinstance(o, canJsonTypes)
    if not chk and raiseName:
        raise Exception('need isinstance({}, {}), but isa {}'.format(raiseName, canJsonTypes, type(o)))

    return chk


class TYPE(object):
    """ just useing in var's TYPE, then can esay lookup var's defines by IDE,
        exam1: str_x= TYPE and str and str_x
        exam2: objAtCls_y= TYPE and Cls and objAtCls_y
    """
    pass

class UndefCls(object):
    """ like js's Undef """
    def __init__(self, name='None'):
        self.__Name__ = name
    def __getattr__(self, item):
        raise AttributeError("'{!r}' has no attribute '{}'".format(self, item))
    def __repr__(self):
        return "_<UndefCls obj at {} #{}>".format(id(self), self.__Name__)
    def __nonzero__(self):
        return False
    def __eq__(self, other):
        return isinstance(other, UndefCls)
    def __ne__(self, other):
        return not self.__eq__(other)

Undef = UndefCls()
assert not isJsonItem(Undef), 'ASSERT: not isJsonItem(Undef)'
assert (Undef == UndefCls('xxx')) == True, "(Undef == UndefCls('xxx')) == True"
assert (Undef != UndefCls('xxx')) == False, "(Undef != UndefCls('xxx')) == False"

class _SymbolHelper(object):
    pass

class Symbol(str):
    """ like js's Symbol """
    def __new__(cls, __Name__=None):
        __HelperObj__ = _SymbolHelper()
        __SymbolStr__ = "_<_SymbolHelper obj at {} #{}>".format(id(__HelperObj__), __Name__)
        self = str(__SymbolStr__)
        return self

    @classmethod
    def __IsinstanceT__(cls, o):
        return isinstance(o, basestring) and o.startswith('_<_SymbolHelper obj at ')

    @classmethod
    def Get(cls, o={}, default=Undef, name=None):
        assert isinstance(o, dict), 'Symbol.Get(o), o must isa dict, but {}'.format(type(o))
        if name:
            finds = [v for k, v in o.items() if
                Symbol.__IsinstanceT__(k) and k.endswith(name)
            ]
        else:
            finds = [v for k, v in o.items() if
                     Symbol.__IsinstanceT__(k)
            ]
        return finds[0] if len(finds)!=0 else default

    @classmethod
    def Set(cls, o={}, value=Undef, name=None):
        assert isinstance(o, dict), 'Symbol.Get(o), o must isa dict, but {}'.format(type(o))
        if name:
            finds = [k for k, v in o.items() if
                Symbol.__IsinstanceT__(k) and k.endswith(name)
            ]
        else:
            finds = [k for k, v in o.items() if
                     Symbol.__IsinstanceT__(k)
            ]
        key = Symbol() if len(finds)==0 else finds[0]
        o[key] = value
        return o

class AttrIf(object):     # 属性判断
    @staticmethod
    def objbuiltin(attr):   # 判断属性是否为系统内建: r"^__[a-z]+__$"
        return re.match(r"^__[a-z]+__$", attr) is not None

    @staticmethod
    def builtin(attr):  # 判断属性是否为用户内建: r"^_[A-Z][a-z]+_$"
        return re.match(r"^_[A-Z][a-z]+_$", attr) is not None

    @staticmethod
    def special(attr):  # 判断属性是否为用户特殊: r"^[a-zA-Z]+\w+__$"
        return re.match(r"^_[A-Z][a-z]+__$", attr) is not None

    @staticmethod
    def extend(attr):  # 判断属性是否为用户扩展: r"^[a-zA-Z]+\w+[a-zA-Z]_$"
        return re.match(r"^[a-zA-Z]+\w+[a-zA-Z]_$", attr) is not None
# end class

class ObjGet(object):  # [实例* 类cls* 所有all*] * [变量vars 方法methods 属性attrs]
    @staticmethod
    def attrs(obj, regMatch='.', is_t=False, limit_callable=None):
        ls = dir(obj)
        attrs = []
        if regMatch == '.' and is_t:
            regMatch = r'^[A-Z]\w+$'
        for i in ls:
            if re.match(r'^__\w+__$', i):
                continue
            if not re.match(regMatch, i):
                continue
            if limit_callable!=None and callable(getattr(obj, i))!=limit_callable:
                continue
            attrs.append(i)
        return attrs

    @staticmethod
    def name(objStr):
        return objStr.split(' ')[1].strip('>')

    @staticmethod
    def methods(obj, ifNotObjbuiltin=True):   # 实例方法(self), 默认不包括objbuiltin
        retMethods = []
        for i in dir(obj):
            iObj = getattr(obj, i)
            if not hasattr(iObj, '__call__'):
                continue
            try:
                iargs = inspect.getargspec(iObj).args
            except BaseException as errObj:
                continue    # 注: 当为i='__class__'时，getargspec(iObj)会报错，故在此加异常处理

            if iargs[0] != 'self':
                continue
            if ifNotObjbuiltin and AttrIf.objbuiltin(i):
                continue
            retMethods.append(i)
        return retMethods
# end class

def obj_getPubKeys(o):
    return [k for k,v in o.__dict__.items() if k[0]!='_']

def obj_getPubValues(o):
    return [v for k,v in o.__dict__.items() if k[0]!='_']

def obj_getPubItems(o):
    return {k:v for k,v in o.__dict__.items() if k[0]!='_'}

def isSpecialAttr(attr=''):
    return bool(attr[:2]+attr[-2:]=='____')

def isinstanceT(o, cls):
    if cls in [str, unicode]:
        cls = basestring  # 放宽py2的字符串类型检查
    if hasattr(cls, '__IsinstanceT__'):
        return cls.__IsinstanceT__(o)
    else:
        return isinstance(o, cls)

def isSubCls(itype, subClsOf=types.TypeType):
    if not issubclass(type(itype), types.TypeType): # first need isa cls
        return False
    return True if subClsOf==types.TypeType else issubclass(itype, subClsOf)

def isFn(o):
    return hasattr(o, '__call__')



def jsonItem(o, msg):
    if not isJsonItem(o):
        raise Exception('%s: type(obj)=%s must isa _jsonItemType' % (msg, type(o)))
    return o

def json_t2o(t, **kw):
    assert isinstance(t, six.text_type), "isinstance(t, six.text_type), but t={!r}".format(t)
    return json.loads(t, **kw)

def json_o2t(o, ensure_ascii=False, indent=None, **kw):
    return json.dumps(o, ensure_ascii=ensure_ascii, indent=indent, **kw)


def jpFinds(jsDc, jsPath, onlyone=None, notNull=False, onlyoneAuto=True, dftRaise=True, dft=Undef):
    """
        print jsFinds({'foo': [{'baz': 1}, {'baz': 2}]}, 'foo[*].baz') #=> [1, 2]
        print jsFinds({'foo': [{'baz': 1}, {'baz': 2}]}, 'foo[0].baz') #=> 1
    """
    #
    if (not jsDc) or (not jsPath):
        raise Exception('#(not jsDc) or (not jsPath), jsDc={!r}, jsPath={!r}'.format(jsDc, jsPath))
    try:
        jsonpath_expr = jpath.parse(jsPath)
        res = [match.value for match in jsonpath_expr.find(jsDc)]
        if len(res) == 0 and notNull:
            raise Exception('#len(res)==0')
        if onlyone or (onlyone == None and onlyoneAuto and (('*' not in jsPath) and ('?' not in jsPath))):
            if len(res) == 1:
                return res[0]
            if dftRaise:
                assert False, 'assert len(res)==1, but res={!r}'.format(res)
            else:
                return dft
        return res
    except Exception as errObj:
        raise Exception('jsPath=%r err=%s' % (jsPath, errObj))


def stackUpFind__Symbol__():
    """  exam: stackUpFind(lambda i: i[0].f_locals.get('kw', {}).get('__Symbol__')) """
    stacks = inspect.stack()
    for i in range(len(stacks)):
        find = Symbol.Get(stacks[i][0].f_locals.get('kw', {}), default=Undef)
        if find!=Undef:
            return find
    return Undef


def KwName(func, *extChkFns):
    def wrapper(*args, **kw):
        fnName = func.__name__
        __Symbol__ = Symbol.Get(kw, default=Undef)
        Symbol.Set(kw, fnName if __Symbol__==Undef else '{}-{}'.format(__Symbol__, fnName))
        if extChkFns:
            for extChkFn in extChkFns:
                extChkFn(kw)
        stackLevel = len(Symbol.Get(kw).split('-'))
        assert len(args) >= 1, 'len(args={!r}) >= 1, but is <{}>'.format(args, len(args))
        log("{p}#{s} {f}(*{a}, **{k})".format(
            p=" "*stackLevel,
            s=stackLevel, f=func.__name__,
            a=stred_brief(args if isJsonItem(args[0]) else args[1:]),
            k=stred_brief({k:v for k, v in kw.items() if not Symbol.__IsinstanceT__(k)})
        ))
        # kw.update({'AX': lambda val, msg: AX(val, msg, debug=None, Utils=DictObject(globals()), kw=kw)})
        return func(*args, **kw)
    return wrapper

def AXDbg(val, msg, debug=True, kw={}):
    return AX(val, msg, debug=debug, Utils=DictObject(globals()), kw=kw)

def KwNameGet(kw, notSpilit=True):
    value = Symbol.Get(kw, default=Undef)
    return value if notSpilit else value.split('-')

def err_detail(errObj, ifDetail=True):
    assert isinstance(errObj, BaseException), \
        "assert isinstance(errObj, BaseException), but isa {}".format(type(errObj))
    return '%s\n%s' % (errObj, traceback.format_exc()) if ifDetail else '{}'.format(errObj)

def tm_str2stamp(s, fmt, isSec=True):
    """ eg. .('2018-01-09 20:31:02', '%Y-%m-%d %H:%M:%S') -> 1515501
         #http://blog.sina.com.cn/s/blog_b09d460201018o0v.html """
    return time.mktime(time.strptime(s, fmt))

def tm_stamp2Str(stamp, fmt):
    return time.strftime(fmt, time.localtime(stamp))

def tm_now(retType=float, notMs=True):
    tm = time.time()
    if not notMs:
        tm = tm * 1000
    return retType(tm)

def time_now(fmt='%Y-%m-%d %H:%M:%S', timedelta_={}):
    timeObj = datetime.now()
    if timedelta_:
        timeObj += timedelta(**timedelta_)
    return datetime.strftime(timeObj, fmt)

def tm_nowStr(fmt='%Y%m%d-%H%M%S-%f'):
    return datetime.strftime(datetime.now(), fmt)

def dc_val2key(dc, val):
    ls = [i for i, j in dc.items() if j == val]
    if len(ls) != 0:
        return ls[0]
    else:
        return val

def encode_get(s):
    if not s:
        return "unicode"
    if not isinstance(s, basestring):
        return None
    if isinstance(s, unicode):
        return "unicode"
    else:
        return chardet.detect(s).get('encoding', None)  # s==''时，会return None

def encode_toCn(s):
    if (not isinstance(s, basestring)): return s
    if (encode_get(s) in ['unicode', 'utf-8']):
        return s.encode('GBK')
    else:
        try:
            ret = s.decode('GBK').encode('GBK')
        except Exception as eObj:
            print(str(eObj))
            raise Exception("encode_toCn: {%s}.decode('GBK').encode('GBK'), error={%s}" % (s, eObj))
        return ret


def encode_to(s, typeNew='utf-8'):
    if not isinstance(s, basestring):
        return s
    typeOld = encode_get(s)
    if not typeOld or typeOld==typeNew:
        return s

    if typeOld != 'unicode':
        s = encode_toU(s)

    try:
        ret = s.encode(typeNew)
    except Exception as eObj:
        raise Exception("encode_toU: {%s}.decode(%s), error={%s}" % (s, typeNew, eObj))
    return ret

def encode_toU(s):
    if not isinstance(s, basestring):
        return s
    codeType = encode_get(s)
    if not codeType:
        return codeType
    if (codeType in ['unicode']):
        return s

    try:
        ret = s.decode(codeType)
    except Exception as eObj:
        print(str(eObj))
        raise Exception("encode_toU: {%s}.decode(%s), error={%s}" % (s, codeType, eObj))
    return ret

def stred_brief(val, max=500):
    return _Utils.stred_brief(val, max=max)

def log(msg, tm=None, **kw):
    tm = tm if tm else tm_nowStr('%Y%m%d-%H%M%S')
    print('[{}] {}'.format(tm, msg))

Try_Infos_DFT = [3, 1, [2, 5, 10]]
def Try_objParseTryInfos(obj, _TryInfos):
        assert isinstance(_TryInfos, list),\
            "_TryInfos=%s, must isa list"%_TryInfos
        assert len(_TryInfos)==3,\
            "_TryInfos=%s, must len==3"%_TryInfos
        (times, gap, timeouts) = _TryInfos
        assert isinstance(timeouts, list),\
            "timeouts=%s, must isa list"%timeouts
        assert len(timeouts)==3,\
            "timeouts=%s, must len==3"%timeouts
        (timeout0,timeout1,timeout2) = timeouts
        for i in [times, gap, timeout0, timeout1, timeout2]:
            assert isinstance(i,int),\
            "_TryInfos=%s, must all isa int, but %s[0]"\
            %(_TryInfos, [i])
            assert (i>0 and i<=100),\
            "_TryTimes_Gap_Timeouts=%s, must all in (0,100], but %s"\
            %(_TryInfos, i)
        obj._TryTimes = times
        obj._TryGap = gap
        obj._TryTimeouts = timeouts
        return times, gap, timeouts

def Try_withTimes(_TryTimes,_TryGap,_msgPre,_reFunc,_reFKw,_func, *fargs, **fKw):
    """ 当_reFunc==None时，不进行恢复操作 """
    if _reFunc==None:
        _reFunc = str
        _reFKw = {}
    for i in range(_TryTimes):
        try:
            iret = _func(*fargs, **fKw)
            break
        except BaseException as ierrObj:
            ierr = err_detail(ierrObj, ifDetail=False)
            print("    ----> %s() times=%s, ierr={%s}" % (_msgPre, (i+1), ierr))
            if (i+1 < _TryTimes):
                try:
                    _reFunc(**_reFKw)
                except BaseException as jerrObj:
                    jerr = err_detail(jerrObj)
                    print("    ----> %s().%s times=%s, jerr={%s}"
                                    % (_msgPre, _reFunc, (i+1), jerr))
                time.sleep(_TryGap)
    else:
        assert False, "----> %s() Fail. ierr={%s}" % (_msgPre, err_detail(ierrObj))
    return iret


class SysCmd(JsonLike):
    @property
    def cmd(self): return self._cmd
    @property
    def code(self): return self._code
    @property
    def output(self): return self._output

    def __init__(self, cmd=None, encodeTo='utf-8', **kwargs):
        self._cmd = cmd
        self._code = -1
        self._output = ''
        if self._cmd:
            try:
                self._code = 0
                self._output = subprocess.check_output(self._cmd, shell=True)
            except subprocess.CalledProcessError as errObj:
                self._code = errObj.returncode
                self._output = ''
        if encodeTo:
            self._output = encode_to(self._output, encodeTo)

def sys_taskkill(name, killall=True):
    if not name:
        return dict(cmd=name, code=-1, output='')
    if os.name == 'nt':
        cmd = 'taskkill /f /im {}'.format(name)
    else:
        kill = 'killall' if killall else 'kill -9'
        cmd = '{} {}'.format(killname)
    return SysCmd(cmd)

def sys_tasklistFind(findstr):
    if not findstr:
        return dict(cmd=findstr, code=-1, output='')
    if os.name == 'nt':
        cmd = 'tasklist| findstr {}'.format(findstr)
    else:
        cmd = "ps -ef| grep {}| awk '{print $8,$2}'| grep {}".format(findstr, findstr)
    return SysCmd(cmd=cmd)

def fn_argspecStr(fn):
    """ e.g.
        def fn(a, b, c=3, d=4, **kwargs):
            pass
        ===>
        '''
        fn(a, b,
            c=3,
            d=4,
            **kwargs
        )
        '''
    """
    fn_argSpec = inspect.getargspec(fn)
    shows_str = ''
    if fn_argSpec.keywords:
        shows_str = '{}{}'.format(
            '**{}'.format(fn_argSpec.keywords),
            shows_str,
        )
    if fn_argSpec.varargs:
        shows = list(fn_argSpec.args)
        shows.append('*{}'.format(fn_argSpec.varargs))
        shows_str = '{}{}'.format(
            ', '.join(shows),
            shows_str,
        )
    else:
        shows_withoutDefaults = []
        shows_withDefaults = []
        args = list(fn_argSpec.args)
        args.reverse()
        len_args = len(args)
        defaults = list((fn_argSpec.defaults or tuple()))
        defaults.reverse()
        len_defaults = len(defaults)
        for i in range(len_args):
            if i < len_defaults:
                shows_withDefaults.insert(0, '='.join([args[i], '{!r}'.format(encode_to(defaults[i]))]))
            else:
                shows_withoutDefaults.insert(0, args[i])
        if shows_withDefaults:
            shows_str = '\n    {}\n    {}'.format(
                '\n    '.join(shows_withDefaults),
                shows_str,
            )
        shows_str = '{}{}'.format(
            ', '.join(shows_withoutDefaults),
            shows_str,
        )
    ret = '{}({}\n):'.format(fn.__name__, shows_str)
    return ret
