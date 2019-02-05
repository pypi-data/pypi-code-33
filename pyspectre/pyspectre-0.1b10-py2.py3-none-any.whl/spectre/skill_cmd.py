from re import findall as findall
# import warnings
# from . import skill_interface as scl
# from .parallel.replwrap_parallel import REPLWrapper_client
# from pexpect.replwrap import REPLWrapper
# from textwrap import wrap as wraptext

"""
low-level interaction for spectre binaries
"""


def exec_scl(pyspectre_obj, cmd, block=True):

    if pyspectre_obj.quit:
        try:
            pyspectre_obj.spectre.run_command('sclQuit()').strip('\r\"')
        except:
            pass
        return

    else:

        # if len(cmd) > 256:
        #     cmd = wraptext(cmd, width=256, break_long_words=False, break_on_hyphens=False)
        #     cmd[:-1] = [item + ' \\' for item in cmd[:-1]]
        # else:
        #     cmd = [cmd]

        try:
            result = pyspectre_obj.spectre.run_command(cmd).strip('\r\"')

            pyspectre_obj.commandct += 1
            if isinstance(result, str):
                return result
            elif isinstance(result, unicode):
                return result.decode('utf8')

        except Exception as e:
            raise RuntimeError('spectre crashed')

            # not going to try restarting, becuase without a proper rollback, can't guarantee consistency"""
            ##################################################################################################
            #
            # if not pyspectre_obj.spectre.child.isalive():
            #     pyspectre_obj.deathcount += 1
            #     if pyspectre_obj.deathcount > pyspectre_obj.restarts:
            #         pyspectre_obj.cleanup()
            #         print("spectre closed unexpectedly... in excess of restart count")
            #         raise e
            # else:
            #     try:
            #         pyspectre_obj.cleanup()
            #     except:
            #         pass
            #     del pyspectre_obj.spectre
            #     pyspectre_obj.spectre = None
            #     pyspectre_obj.quit = False
            #     pyspectre_obj.sclobjs = dict()
            #     warnings.warn("spectre closed unexpectedly. restarting...")
            #     pyspectre_obj.startbinary()
            #     return "spectreCrashed.TryAgain"


"""
    Primitive SKILL functions
"""


def setattribute(pyspectre_obj, obj, attrname, attrval, block=True):
    # obj = resolve(pyspectre_obj,objname)
    if attrval == 'nil' or attrval == 't':
        result = exec_scl(pyspectre_obj, 'sclSetAttribute( \"{}\" \"{}\" {} )'.format(obj, attrname, attrval),
                          block=block)
    else:
        result = exec_scl(pyspectre_obj, 'sclSetAttribute( \"{}\" \"{}\" \"{}\" )'.format(obj, attrname, attrval),
                          block=block)
    if result != "t":
        raise LookupError('failed to set attribute: {}::{}::{}::{} \n'
                          '     make sure it appears in netlist file!'.format(pyspectre_obj.analysis_name, obj,
                                                                              attrname, attrval))
    return


def setresultdir(pyspectre_obj, directory):
    if exec_scl(pyspectre_obj, 'sclSetResultDir(\"{}\")'.format(directory)) != 't':
        raise IOError('failed to set output directory')


"""
get
"""


def getparameter(pyspectre_obj, obj, paramname):
    # obj = resolve(pyspectre_obj,obj)
    result = exec_scl(pyspectre_obj, 'sclGetParameter( \"{}\" \"{}\" )'.format(obj, paramname))
    if not issclparam(result):
        raise LookupError('couldn\'t get specified parameter: \"{}\"'.format(paramname))
    return result


def getattribute(pyspectre_obj, obj, attrname):
    # obj = resolve(pyspectre_obj,obj)
    result = exec_scl(pyspectre_obj, 'sclGetAttribute( \"{}\" \"{}\" )'.format(obj, attrname))
    if result == 'nil':
        raise LookupError('could not get specified attribute:{}'.format(attrname))
    return result


def getanalysis(pyspectre_obj, analname):
    result = exec_scl(pyspectre_obj, 'sclGetAnalysis( \"{}\" )'.format(analname))
    if not issclanal(result):
        raise LookupError('counldn\'t find an analysis by the name: \"{!s}\"'.format(analname))
    return result


def getcircuit(pyspectre_obj, cktname):
    result = exec_scl(pyspectre_obj, 'sclGetCircuit(\"{}\")'.format(cktname))
    if not issclckt(result):
        raise LookupError('couldn\'t find a circuit by the name: \"{}\"'.format(cktname))
    return result


def getinstance(pyspectre_obj, inst):
    result = exec_scl(pyspectre_obj, 'sclGetInstance(\"{}\")'.format(inst))
    if not issclinst(result):
        raise LookupError('couldn\'t get instance with name: \"{}\"'.format(inst))
    return result


def getmodel(pyspectre_obj, model):
    result = exec_scl(pyspectre_obj, 'sclGetModel(\"{}\")'.format(model))
    if not issclmdl(result):
        raise LookupError('couldn\'t get model with name: \"{}\"'.format(model))
    return result


def getprimitive(pyspectre_obj, prim):
    result = exec_scl(pyspectre_obj, 'sclGetPrimitive(\"{}\")'.format(prim))
    if not issclprim(result):
        raise LookupError('couldn\'t get primitive with name: \"{}\"'.format(prim))
    return result


def geterror(pyspectre_obj):
    result = exec_scl(pyspectre_obj, 'sclGetError')
    return findall('\((.+)\)', result)


def getresultdir(pyspectre_obj):
    return exec_scl(pyspectre_obj, 'sclGetResultDir()').strip('\"')


def getpid(pyspectre_obj):
    return exec_scl(pyspectre_obj, 'sclGetPid')


"""
list
"""


def listparameter(pyspectre_obj, obj):
    # obj = resolve(pyspectre_obj,obj)
    result = exec_scl(pyspectre_obj, 'sclListParameter( \"{}\" )'.format(obj))
    return findall('\(\"(.+)\" \"instance\"\)', result)


def listattribute(pyspectre_obj, obj):
    # obj = resolve(pyspectre_obj,obj)
    result = exec_scl(pyspectre_obj, 'sclListAttribute( \"{}\" )'.format(obj))
    return dict(findall('\(\"(.+)\" \"(.+)\"\)', result))


def listanalysis(pyspectre_obj):
    result = exec_scl(pyspectre_obj, 'sclListAnalysis()')
    return dict(findall('\(\"(.+)\" \"(.+)\"\)', result))


def listcircuit(pyspectre_obj):
    result = exec_scl(pyspectre_obj, 'sclListCircuit()')
    return dict(findall('\(\"(.+)\" \"(.+)\"\)', result))


def listinstance(pyspectre_obj, obj=None):
    if not obj:
        result = exec_scl(pyspectre_obj, 'sclListInstance()')
    else:
        result = exec_scl(pyspectre_obj, 'sclListInstance(\"{}\")'.format(obj))
    return dict(findall('\(\"(.+)\" \"(.+)\"\)', result))


def listmodel(pyspectre_obj, obj=None):
    if not obj:
        result = exec_scl(pyspectre_obj, 'sclListModel()')
    else:
        result = exec_scl(pyspectre_obj, 'sclListModel(\"{}\")'.format(obj))
    return dict(findall('\(\"(.+)\" \"(.+)\"\)', result))


def listnet(pyspectre_obj):
    result = exec_scl(pyspectre_obj, 'sclListNet()')
    return findall('\((?:\"(.+)\")+\)', result)


def listprimitive(pyspectre_obj):
    result = exec_scl(pyspectre_obj, 'sclListPrimitive()')
    return findall('\(\"(.+)\" \".+\" \".+\"\)', result)


"""
other
"""


def createanalysis(pyspectre_obj, aname="", atype=""):
    result = exec_scl(pyspectre_obj, 'sclCreateAnalysis( \"{}\" \"{}\" )'.format(aname, atype))
    if not issclanal(result):
        IOError('failed to create analysis named \"{}\"'.format(aname))
    return result


def releaseobject(pyspectre_obj, arg):
    result = exec_scl(pyspectre_obj, 'sclReleaseObject(\"{}\")'.format(arg))
    return result


def run(pyspectre_obj, arg):
    # if not issclobj(arg) and arg != 'all':
    #   arg = resolve(pyspectre_obj,arg)
    result = exec_scl(pyspectre_obj, 'sclRun(\"{}\")'.format(arg))
    result = result.split('\r\n')
    if result[-1] != 't':
        raise UnboundLocalError('simulation unsuccessful')
    return result


def runanalysis(pyspectre_obj, arg, block=True):
    result = exec_scl(pyspectre_obj, 'sclRunAnalysis( \"{}\" )'.format(arg), block=block)
    result = result.split('\r\n')
    if result[-1] != 't':
        raise UnboundLocalError('simulation unsuccessful')
    return result


def help(pyspectre_obj):
    return exec_scl(pyspectre_obj, 'sclHelp')


def quit(pyspectre_obj):
    pyspectre_obj.quit = True
    return exec_scl(pyspectre_obj, 'sclQuit')


def mdlregmeasurement(pyspectre_obj):
    return exec_scl(pyspectre_obj, 'mdlRegMeasurement()')


def mdllistaliasmeasurement(pyspectre_obj):
    return exec_scl(pyspectre_obj, 'mdlListAliasMeasurement()')


def mdlrun(pyspectre_obj):
    return exec_scl(pyspectre_obj, 'mdlRun()')


def mdldelmeasurement(pyspectre_obj):
    return exec_scl(pyspectre_obj, 'mdlDelMeasurement()')


"""
helpers
"""


def issclanal(sclobj):
    try:
        return True if sclobj.startswith('sclAnal0x') else False
    except:
        return False


def issclparam(sclobj):
    try:
        return True if sclobj.startswith('sclParam0x') else False
    except:
        return False


def issclinst(sclobj):
    try:
        return True if sclobj.startswith('sclInst0x') else False
    except:
        return False


def issclckt(sclobj):
    try:
        return True if sclobj.startswith('sclCkt0x') else False
    except:
        return False


def issclmdl(sclobj):
    try:
        return True if sclobj.startswith('sclMdl0x') else False
    except:
        return False


def issclprim(sclobj):
    try:
        return True if sclobj.startswith('sclPrim0x') else False
    except:
        return False


def issclobj(sclobj):
    try:
        return True if (sclobj.startswith('scl') and '0x' in sclobj) else False
    except:
        return False
