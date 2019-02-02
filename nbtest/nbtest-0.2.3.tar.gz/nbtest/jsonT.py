# encoding=utf-8

from .future2to3 import *

from .assertpyx import *
from .Utils import TYPE
from . import Utils


import types, re, copy, numbers
from DictObject import DictObject, DictObjectList


_DictObject_getattr_bak = DictObject.__getattr__
def _DictObject_getattr_new(self, item):
    """ ### use like js<undefined>: o.undefined == JsonTUndef ### """
    try:
        return _DictObject_getattr_bak(self, item)
    except AttributeError:
        return JsonTUndefCls(item)
DictObject.__getattr__ = _DictObject_getattr_new
###

_IsDebug = False
def _debug(msg):
    if _IsDebug:
        print(msg)

class _JsonTLib(object):
    @staticmethod
    class Debug(object):
        def __init__(self, debug=False):
            self.debug = debug
        def __call__(self, msg):
            if self.debug:
                print(msg)

JsonTUndefCls = Utils.UndefCls
JsonTUndef = Utils.Undef


JsonTTemp = {}
class _JsonTBase(object):
    ''' use json_likeStructObj=_JsonT(json_likePyDict) to instead json_likePyDict
    
    # define static_JsonT, that property@not_defined is error
    class SquareSucRes(_JsonT):
        """ {"status":1} """
        status = JsonTVar([1])  # assert self.status in [1]
    
    # define JsonTExtendable, that property@not_defined is not error
    class IDataBody(JsonTExtendable):
        """ {"_id":1, "_create_at":"c", "_inserttime":"i", "??other":"??"} """
        _id = JsonTVar.Def(basestring)
        _create_at = JsonTVar.Def(basestring)
        _inserttime = JsonTVar.Def(long, __Must__=False)  # property is not must
    
    # can inherit define_at_class, or define_at_JsonTVar
    class SquareSucResByOneData(SquareSucRes):
        """ {"status":1,
            "data":null|{"_id":1, "_create_at":"c", "_inserttime":"i", "??other":"??"}
        }
        """
        data = JsonTVar.Def(IDataBody, types.NoneType) # property isa None, or like IDataBody
    
    '''
    # __Listi__ = None
    __EXT__ = True            # isPermit(clsKeyExt not in clsDefines)
    def __init__(self, __Name__, __Json__=JsonTUndef, **kw):
        self.__Inited__ = False
        self.__Name__ = __Name__
        if self.__class__.__name__[0].isupper():
            JsonTTemp[self.__Name__] = __Json__
            self.__Name__ += '<{}>'.format(self.__class__.__name__)
        cls = self.__class__
        clsKeys = self.__GetClsKeys__(updVarName=True)
        if __Json__ != JsonTUndef:
            if isinstance(__Json__, (dict, list)):
                inputJson = __Json__
            elif isinstance(__Json__, JsonT):
                inputJson = __Json__.__Json__
            else:
                raise TypeError('%s.__Json__=%r, must isa dict/list or JsonT' % (__Name__, __Json__))
        else:
            inputJson = {}
            for k, v in kw.items():
                if k not in clsKeys and not cls.__EXT__:
                    AX(k, '%s.k must in clsKeys, when not __EXT__' % __Name__).is_in(*clsKeys)
                if v != JsonTUndef:
                    inputJson[k] = v
        self.__MissKey__ = []
        self.__Json__ = inputJson   # TODO: 这里改为用原始的inputJson
        self.__ChkT__(clsKeys, inputJson)  # isa dict, not Dictobject
        # self.__Test__()
        self.__Inited__ = True
        try:
            AX(self, '{}==<kwargs>__Json__'.format(self.__Name__)).isItemsEq(self.__Json__)
        except Exception as e:
            raise Exception(e)
        # if isinstance(self, JsonTListable):
        #     AX(self, '{}==<kwargs>__Json__'.format(self.__Name__)).isSetEq(__Json__)
        # else:
        #     AX(self, '{}==<kwargs>__Json__'.format(self.__Name__)).isItemsEq(__Json__)

    def __ChkT__(self, clsKeys, inputJson):
        cls = self.__class__
        chkT = '<T>'
        if isinstance(self, JsonTListable):
            assert False, 'must not JsonTListable'
        else:
            newJson = {}
            for missKey in (set(clsKeys) - set(inputJson.keys())):
                AX(cls, self.__Name__+'<missKey>').doAttr(missKey).doAttr('__Must__').is_false()
                self.__MissKey__.append(missKey)

            for k, v in inputJson.items():
                if v == JsonTUndef:
                    continue        # jump the 'obj.v == JsonTUndef'
                if k not in clsKeys:
                    AX(cls.__EXT__, '%s: when {k=%r} not in %s, cls.__EXT__ SHOULD:' % (self.__Name__, k, clsKeys)).is_true()
                    self.__setattr__(k, v)
                    newJson[k] = Utils.jsonItem(v, '%s[%s]%s' % (self.__Name__, k, chkT))
                else:
                    clsKeyDef = getattr(cls, k)
                    if Utils.isSubCls(clsKeyDef):
                        clsKeyName = self.__GetClsKeyName__(k)
                        if issubclass(clsKeyDef, JsonTVariableMust):
                            clsKeyDef = JsonTVarMust.Def(clsKeyDef, __Name__=clsKeyName)
                        elif issubclass(clsKeyDef, JsonTVariable):
                            clsKeyDef = JsonTVar.Def(clsKeyDef, __Name__=clsKeyName)
                    newVal = clsKeyDef.chk_types('%s.%s%s' % (self.__Name__, k, chkT), v)
                    if isinstance(newVal, JsonT):
                        newJson[k] = Utils.jsonItem(newVal.__Json__, '%s[%s]%s' % (self.__Name__, k, chkT))
                    else:
                        newJson[k] = Utils.jsonItem(newVal, '%s[%s]%s' % (self.__Name__, k, chkT))
                    self.__setattr__(k, newVal)
        return newJson

    def __GetClsKeyName__(self, k):
        return '%s.%s' % (repr(self.__class__)[len("<class '"):-len("'>")], k)

    def __GetClsKeys__(self, updVarName=False):
        cls = self.__class__
        clsKeys = []
        for k in dir(cls):
            v = getattr(cls, k)
            if Utils.isSpecialAttr(k) or hasattr(dict, k):
                continue
            if isinstance(v, JsonTVar.Def) or Utils.isSubCls(v, JsonTVariable) or Utils.isSubCls(v, JsonTVariableMust):
                clsKeys.append(k)
                if updVarName: # e.g. ATReviews._JsonT.Reviewyoda.GetTask.data
                    v.__Name__ = self.__GetClsKeyName__(k)
        return clsKeys

    def __GetJson__(self):
        return self.__Json__

    # def __repr__(self):
    #     return str(self.__Json__) # "%s #%s" % (object.__repr__(self), self.__Name__)

    # def __getattribute__(self, key):
    #     if key[:2]+key[-2:]!='____':
    #         if (key in self.__MissKey__):
    #             return JsonTUndefCls('%s.%s<opt>' % (self.__repr__(), key))
    #         if key not in dir(self):
    #             return JsonTUndefCls('%s.%s<undef>' % (self.__repr__(), key))
    #     return object.__getattribute__(self, key)

    def __setattr__(self, key, value):
        if key != '__Inited__' and self.__Inited__:
            raise Exception('cannot use %s.__setattr__() after .__Inited__' % self.__Name__)
        return object.__setattr__(self, key, value)

    def __Test__(self):
        raise TypeError('%s: have not rewrite %s.__Test__' % (self.__Name__, self.__class__.__name__))

class JsonT(_JsonTBase, DictObject):
    def __init__(self, __Name__, __Json__=JsonTUndef, **kw):
        AX(__Name__, '__Name__').is_instance_of(basestring)
        __Json__ = __Json__ if __Json__ else kw
        AX(__Json__, __Name__).is_instance_of(dict)
        DictObject.__init__(self, __Json__)
        _JsonTBase.__init__(self, __Name__, __Json__)


class JsonTExtendlimit(JsonT):
    __EXT__ = False

class JsonTVar(object):
    class Def(object):
        __MustDft__ = False
        def __init__(self, *types_, **kwargs):
            self.__Name__ = None
            if kwargs.has_key("__Name__"):
                self.__Name__ = kwargs["__Name__"]
            self.types_ = types_
            self.typeNames = []
            for i in types_:
                self.typeNames.append(i.__name__ if hasattr(i, '__name__') else i)

            self.typeChks = []
            cls = self.__class__
            AX(types_, 'types_').is_not_empty()
            for i in range(len(types_)):
                itype = types_[i]

                if issubclass(type(itype), types.ListType):
                    AX(itype, 'itype').is_not_empty()
                    if itype[0] == list:
                        if len(itype) == 1:  # JsonTVar.Def([list])
                            self.typeChks.append([cls.chk_list_eachNoLimit, None])
                        else:
                            AX(itype, 'itype').is_length(2)
                            if isinstance(itype[1], list):  # JsonTVar.Def([list, list])
                                AX(itype[1], 'itype[1]<chk_list_eachInList>').is_not_empty()
                                self.typeChks.append([cls.chk_list_eachInList, itype[1]])
                            elif Utils.isSubCls(itype[1]): # JsonTVar.Def([list, cls])
                                self.typeChks.append([cls.chk_list_eachInCls, itype[1]])
                            else:
                                raise TypeError('itype=%r is types [list, *], * must isa: list or class' % itype)
                    else:   # JsonTVar.Def(list)
                        self.typeChks.append([cls.chk_list_enum, itype])  # isa list_enum
                else:  # JsonTVar.Def(cls<!list>)
                    AX(itype, '{!r} isa class<!list>'.format(itype)).doCalled(type).is_not_equal_to(types.ListType)
                    self.typeChks.append([cls.chk_cls_exceptList, itype])
                # else:
                #     raise TypeError('itype=%r must types in: cls<!list> list_enum [list] [list,list] [list,cls]' % itype)

            __Must__ = kwargs.get('__Must__', self.__MustDft__)
            AX(__Must__, '__Must__').is_instance_of(bool)
            self.__Must__ = __Must__

        def __repr__(self):
            return "%s #%s" % (object.__repr__(self), self.__Name__)

        def __getattr__(self, item):
            raise AttributeError("%r object has no attribute %r" % (self.__repr__(), item))

        def __nonzero__(self):  # e.g. bool(JsonT('',dict(var_option=JsonTUndef)).var_option) == False
            return False

        def __SetMust__(self, __Must__):
            AX(__Must__, '__Must__').is_instance_of(bool)
            self.__Must__ = __Must__
            return self

        def chk_types(self, name, targetVal):
            errmsgs = ['']
            for i in range(len(self.typeChks)):
                imethod, iarg = self.typeChks[i]
                try:
                    return imethod(name, targetVal, iarg)
                except AXError as e1:
                    errmsg = 'AXError: %s' % e1
                    errmsgs.append(errmsg)
                    AXConfig.log(AXBuild(None, debug=_IsDebug), errmsg)
                except AXOtherError as e2:
                    errmsg = 'AXOtherError: %s' % e2 #_assertpyx._ax_errDetail(e2)
                    errmsgs.append(errmsg)
                    AXConfig.log(AXBuild(None, debug=_IsDebug), errmsg)
                # except BaseException as e3:
                #     errmsg = 'OtherError: %s' % _assertpyx._ax_errDetail(e3)
                #     errmsgs.append(errmsg)
                #     AXConfig.log(AXBuild(None, debug=_IsDebug), errmsg)
            else:
                errmsgSum = '%s: not types in %s, errmsgs={%s\n}' % (name, self.typeNames, '\n    '.join(errmsgs))
                raise Exception(errmsgSum)

        @classmethod
        def _chkIsinstance(cls, name, targetVal, arg):
            if Utils.isSubCls(arg, JsonT):
                # if targetVal == None:   # json_empty_object is 'null'
                #     return None
                AX(targetVal, name, debug=False).doCalled(Utils.isinstanceT, (dict, JsonT)).is_true()
                return arg(name, targetVal)
            elif Utils.isSubCls(arg, JsonTListable):
                # if targetVal == []:     # json_empty_array is '[]'
                #     return []
                AX(targetVal, name, debug=False).doCalled(Utils.isinstanceT, list).is_true()
                return arg(name, targetVal)
            else:
                AX(targetVal, name, debug=False).doCalled(Utils.isinstanceT, arg).is_true()
                return targetVal
        @classmethod
        def chk_cls_exceptList(cls, name, targetVal, arg):
            return cls._chkIsinstance(name, targetVal, arg)
        @classmethod
        def chk_list_enum(cls, name, targetVal, arg):
            AX(targetVal, name, debug=False).is_in(*arg)
            return targetVal
        @classmethod
        def chk_list_eachNoLimit(cls, name, targetVal, arg=None):
            AX(targetVal, name, debug=False).is_instance_of(list)
            return targetVal
        @classmethod
        def chk_list_eachInCls(cls, name, targetVal, arg):
            retVal = []
            AX(targetVal, name, debug=False).is_instance_of(list)
            for i in range(len(targetVal)):
                itarget = targetVal[i]
                retVal.append(cls._chkIsinstance('%s[%s]' % (name, i), itarget, arg))
            return retVal
        @classmethod
        def chk_list_eachInList(cls, name, targetVal, arg):
            retVal = []
            AX(targetVal, name, debug=False).is_instance_of(list)
            for i in range(len(targetVal)):
                itarget = targetVal[i]
                AX(itarget, '%s[%s]' % (name, i), debug=False).is_in(*arg)
                retVal.append(itarget)
            return retVal
    Dict = TYPE and dict and Def(dict)
    List = TYPE and list and Def(list)
    Text = TYPE and six.text_type and Def(six.text_type)
    Float = TYPE and float and Def(float)
    Integral = TYPE and six.integer_types and Def(six.integer_types)
    Bool = TYPE and bool and Def(bool)


class JsonTVarMust(JsonTVar):
    class Def(JsonTVar.Def):
        __MustDft__ = True
    Dict = TYPE and dict and Def(dict)
    List = TYPE and list and Def(list)
    Text = TYPE and six.text_type and Def(six.text_type)
    Float = TYPE and float and Def(float)
    Integral = TYPE and six.integer_types and Def(six.integer_types)
    Bool = TYPE and bool and Def(bool)


class JsonTListable(DictObjectList):
    __Listi__ = JsonTVar.Def(JsonT)
    def __init__(self, __Name__, __Json__):
        AX(__Json__, __Name__).is_instance_of(list)
        inputJson = __Json__
        chkT = '<T>'
        newJson = []
        for i in range(len(inputJson)):
            v = inputJson[i]
            iname = '%s[%s]%s' % (__Name__, i, chkT)
            clsKeyDef = getattr(self.__class__, '__Listi__')
            AX(clsKeyDef, iname).is_instance_of(JsonTVar.Def)
            newVal = clsKeyDef.chk_types(iname, v)
            newJson.append(Utils.jsonItem(newVal, iname))
        DictObjectList.__init__(self, newJson)

class JsonTVariableMust(object):
    """ class ExamA(JsonT):
            class var1(JsonT, JsonTVariable):
                var11 = JsonTVar.Def(int)
            var2 = JsonTVar.Def(int)
        a = ExamA(dict(var2=2, var1=dict(var11=11)))
    """
    __Must__ = True

class JsonTVariable(object):
    """ JsonTVariable<must=False> """
    __Must__ = False


class JsonTEnum(list):
    pass

def jsonTNotoverwireErr():
    raise Exception('jsonTNotoverwireErr')

def jsonTDictobjGet(dcOld, path):
    """ fn({'a':{'aa', 10}}, 'a.aa') => 10 """
    tmp = DictObject.objectify(dcOld)
    pathNodes = path.split('.')
    for i in range(len(pathNodes)):
        pathNode = pathNodes[i]
        if not isinstance(tmp, dict):
            _debug('tmp-not-isa-dict')
            return JsonTUndef
        if not tmp.has_key(pathNode):
            _debug('tmp-not-has_key-%s' % pathNode)
            return JsonTUndef
        tmp = tmp[pathNode]
    return tmp

def jsonTDictobj(dcOld, path=JsonTUndef, val=JsonTUndef):
    """ dcOld = {"a":{"a1": 1}, "b": None}
    AX(dcOld, 'dcOld-1').is
    jsonTDictobj({"a":{"a1": 1}, "b": None}, {'aa.a2':22, 'a.a2.a3': 3, 'b.b1': 20})
     == {"a", {"a1": 1, "a2": {"a3": 3}}, "aa": {"a2": 22}, "b": {"b1": 20}} 
    """
    obj = DictObject.objectify(dcOld)
    if path==JsonTUndef or val==JsonTUndef:
        return obj

    pathNodes = path.split('.')         # e.g. ['a', 'a2', 'a3']
    nodeIndexMax = len(pathNodes) - 1   # e.g. 2
    nodeTail = pathNodes[nodeIndexMax]  # eg. ['a3']

    # use like HTTP.PATCH
    tmpObj = obj
    for nodeIndex in range(len(pathNodes)-1):    # e.g. nodeIndex = 1
        node = pathNodes[nodeIndex]
        tmpObj_get = tmpObj.get(node, JsonTUndef)  # e.g. tmpObj = obj['a'].get('a2')
        if not isinstance(tmpObj_get, dict):
            tmpObj[node] = {}
        tmpObj = tmpObj[node]
    tmpObj[nodeTail] = val
    return obj
_test_dcOld = {"a":{"a1": 11}, "b": None}
AX(_test_dcOld, '_test_dcOld-1').doCalled(jsonTDictobj, 'a.a1', {'aa1': 111}).isItemsEq(
    {"a": {"a1": {'aa1': 111}}, "b": None}
)
AX(_test_dcOld, '_test_dcOld-1').doCalled(jsonTDictobj, 'aa.a2', 12).isItemsEq(
    {"a": {"a1": 11}, "aa": {"a2": 12}, "b": None}
)
AX(_test_dcOld, '_test_dcOld-2').doCalled(jsonTDictobj, 'a.a2.aa3', 113).isItemsEq(
    {"a": {"a1": 11, "a2": {"aa3": 113}}, "b": None}
)
AX(_test_dcOld, '_test_dcOld-3').doCalled(jsonTDictobj, 'b.b1', 21).isItemsEq(
    {"a": {"a1": 11}, "b": {"b1": 21}}
)
AX(_test_dcOld, '_test_dcOld-4').doCalled(jsonTDictobj, 'a', {'a3': 13}).isItemsEq(
    {"a": {"a3": 13}, "b": None}
)


def jsonTDictobjPatch(oldDictobj, newDict, pathPre='', dcReplaces=[], lsPatchs=[], debug=False):
    debug = _JsonTLib.Debug(debug)
    oldDictobj = DictObject.objectify(oldDictobj)

    for k, v in newDict.items():
        pathFull = pathPre + k
        if pathFull=='a.a1':
            pass
        if not isinstance(v, dict):
            debug('%s=%r' % (pathFull, v))
            if isinstance(v, list) and (pathFull in lsPatchs):
                vOld = jsonTDictobjGet(oldDictobj, pathFull) or []
                AX(vOld, "lsPatchs<{}>'s oldValue must list".format(pathFull)).is_instance_of(list)
                vNew = list(vOld)
                vNew.extend(v)
                oldDictobj = jsonTDictobj(oldDictobj, pathFull, vNew)
                # debug('%r.%s == %r' % (id(oldDictobj), pathFull, eval('oldDictobj.' + pathFull)))
            else:
                oldDictobj = jsonTDictobj(oldDictobj, pathFull, v)
                # debug('%r.%s == %r' % (id(oldDictobj), pathFull, eval('oldDictobj.' + pathFull)))
        else:
            if pathFull in dcReplaces:  # use <replace> when top_level(pathPre=='')
                debug('oldDictobj.__setitem__(%r, %r)' % (pathFull, v))
                oldDictobj = jsonTDictobj(oldDictobj, pathFull, v)
            else:
                pathPreNew = pathFull + '.'
                debug('jsonTDictobjPatch(oldDictobj, pathPre=%r, debug=%r, newDict=%r)' \
                      % (pathPreNew, debug.debug, v))
                oldDictobj = jsonTDictobjPatch(
                    oldDictobj, newDict=v, pathPre=pathPreNew, dcReplaces=dcReplaces, lsPatchs=lsPatchs, debug=debug.debug
                )
    return oldDictobj
_test_dcOld = DictObject({"a": {"a1": [11], "a2": {"a21": 121}}, "b": {"b1": 21}})
AX(_test_dcOld, '_test_dcOld-1')\
    .doCalled(jsonTDictobjPatch, {'a':{"a1": [11.2], 'a3':13, 'a2': {'a22': 122}}, 'b':{'b2':22}},
              dcReplaces=['b'], lsPatchs=['a.a1'])\
    .isItemsEq({"a": {"a1": [11, 11.2], "a2": {"a21": 121, "a22": 122}, "a3": 13}, "b": {"b2": 22}})


if __name__ == '__main__':
    def _if_main(): pass

    class SquareSucRes(JsonT):
        """ {"status":1} """
        status = JsonTVar.Def([1])  # assert self.status in [1]

    lsT = JsonTListable('ls0', [SquareSucRes('suc0', dict(status=1))])
    print(123)
