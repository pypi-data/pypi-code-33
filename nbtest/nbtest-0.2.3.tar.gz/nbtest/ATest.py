# encoding=utf-8

from nbtest.future2to3 import *

import os, sys, json, types, re
from DictObject import DictObject

from parameterized import param
from nbtest.assertpyx import AX, AXConfig
from nbtest import Utils

class KcRet(object):
    __Rets__ = DictObject({})
    def __init__(self, _lambda):
        self._lambda = _lambda
    def __call__(self, *args, **kwargs):
        return self._lambda(KcRet.__Rets__)

def Kc(Id, Text, BizKeyActions, times=1):
    """ exam:
        Kc('ts2', u'Expecter生成预期值，并与实际值进行校验', [
            ('ts2_1', None, 'new_fulltask', dict(
                BK_FN=Ctx.api.Audit_VdWm,
                taskId=KcRet(lambda: rets: rets.old_fulltask.task._id),
                denys=[denys.key2Val(kwObj._deny)], timeliness=EFTimeliness.key2Val(kwObj._timeliness),
                _old_fulltask=KcRet.old_fulltask, _notSkipAudit=False
            ))
        ])
    """
    err = ''
    for i in range(1,times+1):
        print('\n  ====>>>>  {}<times={}>: {}'.format(Id, i, Text))
        try:
            for j_BizKeyAction in BizKeyActions:
                AX(j_BizKeyAction, 'j_BizKeyAction').is_length(4)
                j_Id, j_Text, j_RetVar, j_BizKeyRunner = j_BizKeyAction
                j_RetVar = j_RetVar or j_Id
                print('  ---->>>>  {}: {}'.format(j_Id, j_Text))
                bizkeyKwargs = {}
                for _k, _v in j_BizKeyRunner.items():
                    if _k=='BK_FN':
                        continue
                    bizkeyKwargs[_k] = _v if not isinstance(_v, KcRet) else _v.__call__()
                KcRet.__Rets__[j_RetVar] = j_BizKeyRunner['BK_FN'](**bizkeyKwargs)
            break
        except Exception as err:
            print(err)
    else:
        raise Exception(Utils.err_detail(err))



def cdProjPath(subProj=''):
    projPath = os.getenv('TCLSPACE')
    if subProj:
        projPath = os.path.join(os.getenv('TCLSPACE'), subProj)
    projPath = os.path.abspath(projPath)
    if os.path.abspath(os.getcwd()) != projPath:
        os.chdir(projPath)
    print('projPath=', os.path.abspath(os.getcwd()))


def _fmt_args_kwargs(*some_args, **some_kwargs):
    """Helper to convert the given args and kwargs into a string."""
    if some_args:
        out_args = str(some_args).lstrip('(').rstrip(',)')
    if some_kwargs:
        out_kwargs = ', '.join([str(i).lstrip('(').rstrip(')').replace(', ',': ') for i in [
                (k,some_kwargs[k]) for k in sorted(some_kwargs.keys())]])

    if some_args and some_kwargs:
        return out_args + ', ' + out_kwargs
    elif some_args:
        return out_args
    elif some_kwargs:
        return out_kwargs
    else:
        return ''


def _testfunc_name(func, num, param_): #nosetests
    return "%s_%02d" % (func.__name__, (num+1))

def _testfunc_doc(func, num, param_):
    pre = ''
    if '--collect-only' in sys.argv:
        pre = _testfunc_name(func, num, param_)
    param_values = param_.kwargs.get('__NAME__') or param_.kwargs.values()
    return "%s # %s" % (pre, param_values)


def mbtPict(name, limit='', path=None, **kw): #nosetests
    # @parameterized.expand(input=[
    #     param(a=1, b=3, c=5),
    #     param(a=2, b=4, c=6),
    # ], testcase_func_name=ATest._testfunc_name, doc_func=ATest._testfunc_doc)
    return Mbt(name, limit=limit, path=path, **kw).parametrized

def mbtPict_pytest(cls, name, limit='', path='.', **kw):
    """ @pytest.mark.parametrize(argnames), argvalues, ids=MbtParametrizeIdfn(argnames)) """
    return Mbt(name, limit=limit, path=path, **kw).parametrized

class MbtParametrizeIdfn(object):
    """ {PICT} https://github.com/Microsoft/pict/blob/master/doc/pict.md """
    def __init__(self, argnames):
        self.argnameLs = argnames.split(',')
        self._argnameNum = len(self.argnameLs)
        self._seqCount = 0
    def __call__(self, i_val):
        i_seq = self._seqCount % self._argnameNum
        self._seqCount += 1
        return '%s=%s' % (self.argnameLs[i_seq], i_val)

class Mbt(object):
    __Force__ = False
    __DftPath__ = None
    @classmethod
    def SetDftPath(cls, dftPath):
        cls.__DftPath__ = os.path.abspath(dftPath)
        print('Mbt.__DftPath__=', cls.__DftPath__)

    def __init__(self, name, limit='', path=None, **kw):
        # _violate = EFViolate.__Keys__()
        # _deny = EFDeny_CIL1.__Keys__()
        # _LIMIT = 'IF [_deny] = "Pass" THEN [_violate] = "No";'
        try:
            self.name = name
            self.path = path or self.__class__.__DftPath__
            self.modeloutFname = os.path.abspath('%s/%s.MO.txt ' % (self.path, self.name))
            self.modelinFname = os.path.abspath('%s/%s.MI.txt ' % (self.path, self.name))
            self.argv_testmatch = [_i[len('--testmatch='):] for _i in sys.argv if _i.startswith('--testmatch=')]
            self.argv_testmatch = self.argv_testmatch[0] if self.argv_testmatch else '^$'

            if not re.match(self.argv_testmatch, name):
                self.parametrized = dict(input=[])
                return

            if (self.__class__.__Force__ or (not os.path.exists(self.modelinFname))):
                modContentLs = []
                self._cmd = 'PICT %s > %s /d:`\n' % (self.modelinFname, self.modeloutFname)
                print("    Mbt(%r)" % self._cmd)
                modContentLs.append('# {}'.format(self._cmd))
                for k in sorted(kw.keys()):
                    v = []
                    for _x in kw[k]:
                        v.append('|'.join([str(_i) for _i in _x]) if isinstance(_x, set) else _x) #Separator for aliases (default: |)
                    modContentLs.append('{}: {}'.format(k, '` '.join(v)))
                modContentLs.append('\n' + limit)
                self._modContents = '\n'.join(modContentLs)

                # modelinput
                with open(self.modelinFname, 'w+') as f:
                    f.write(self._modContents)

                # modeloutput
                os.system(self._cmd)

            # parse_modelout
            self.parametrized = self._parsePictModelout(self.modeloutFname)
        except Exception as e:
            print(Utils.err_detail(e))
            raise Exception(Utils.err_detail(e))


    def _strToJsonbasedata(self, s):
        try:
            ret = json.loads('[{s}]'.format(s=s))[0]
        except ValueError as e:
            ret = s
        return ret

    def _parsePictModelout(self, filename):
        # PICT.out.txt => pytest.parmas # ~开头的仅代表无效类，实际应用中应去掉
        # [argnames, argvalues<[argvaluetuple]>]

        with open(filename) as _f:
            pictOut = _f.read()
        pictOutLines = pictOut.split('\n')
        argnameLs = pictOutLines[0].split('\t')
        argNum = len(argnameLs)
        argsvalueLs = []
        input_params = []
        for _i in range(1, len(pictOutLines)):
            if not pictOutLines[_i]:
                break
            _args = pictOutLines[_i].split('\t')
            assert len(_args) == argNum, \
                'ASSERT: _i=%r _args=%r: {len(_args)=%s} == {argNum=%s}' % (_i, _args, len(_args), argNum)
            _argsvalue = [_i]   # 插入__ID__=_i 1-based
            _input_param_dict = dict(__ID__=_i)
            _args_get = pictOutLines[_i].split('\t')
            for _j in range(len(_args_get)):
                _argName = argnameLs[_j]
                _arg_get = _args_get[_j]
                if _arg_get[0]=='~':
                    _arg_get = _arg_get[1:]  # ~开头的仅代表无效类，实际应用中应去掉
                _argValue = self._strToJsonbasedata(_arg_get)
                _argsvalue.append(_argValue)
                _input_param_dict[_argName] = _argValue
            argsvalueLs.append(tuple(_argsvalue))
            input_params.append(param(**_input_param_dict))
        argnameLs.insert(0, '__ID__')
        argnames = ','.join(argnameLs)
        return dict(input=input_params, doc_func=_testfunc_doc,
                    testcase_func_name=_testfunc_name,
                    )

    def _parsePictModelout_pytest(self, filename):
        # PICT.out.txt => pytest.parmas # ~开头的仅代表无效类，实际应用中应去掉
        # [argnames, argvalues<[argvaluetuple]>]

        with open(filename) as _f:
            pictOut = _f.read()
        pictOutLines = pictOut.split('\n')
        argnameLs = pictOutLines[0].split('\t')
        argNum = len(argnameLs)
        argsvalueLs = []
        for _i in range(1, len(pictOutLines)):
            if not pictOutLines[_i]:
                break
            _args = pictOutLines[_i].split('\t')
            assert len(_args) == argNum, \
                'ASSERT: _i=%r _args=%r: {len(_args)=%s} == {argNum=%s}' % (_i, _args, len(_args), argNum)
            _argsvalue = [_i]   # 插入__ID__=_i 1-based
            for _j in pictOutLines[_i].split('\t'):
                _arg = _j if _j[0]!='~' else _j[1:]   # ~开头的仅代表无效类，实际应用中应去掉
                _argsvalue.append(self._strToJsonbasedata(_arg))
            argsvalueLs.append(tuple(_argsvalue))
        argnameLs.insert(0, '__ID__')
        argnames = ','.join(argnameLs)
        return dict(argnames=argnames, argvalues=argsvalueLs, ids=MbtParametrizeIdfn(argnames))

class BkwCls(object):
    pass


def _AX_IfDebugFn(istack):
    return isinstance(istack[0].f_locals.get('self'), BkwCls) and re.match(r'[A-Z]\w+_\w+', istack[3])
AXConfig.addAXDebugFn('ATest', _AX_IfDebugFn)