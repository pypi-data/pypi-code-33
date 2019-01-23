import jpy
import wrapt
import dill
import base64
import inspect

__all__ = ["Calendars", "DBTimeUtils", "plot", "QueryScope", "TableTools", "TableManagementTools"]




class DbWrapper(wrapt.ObjectProxy):
    def executeQuery(self, query):
        pickled = dill.dumps(query)
        newQuery = PythonRemoteQuery(pickled)
        res = self.__wrapped__.executeQuery(newQuery)
        return self.inflateResult(res)

    def pushClass(self, classToDefine):
        if not inspect.isclass(classToDefine):
            raise TypeError(classToDefine + " is not a class!")
        name = classToDefine.__name__
        pickled = dill.dumps(classToDefine)
        pushQuery = PythonPushClassQuery(name, pickled)
        self.__wrapped__.executeQuery(pushQuery)

    def eval(self, string):
        evalQuery = PythonEvalQuery(string)
        self.__wrapped__.executeQuery(evalQuery)

    def fetch(self, name):
        fetchQuery = PythonEvalQuery(name)
        res = self.__wrapped__.executeQuery(fetchQuery)
        return self.inflateResult(res)

    def inflateResult(self, obj):
        if isinstance(obj, jpy.get_type("com.illumon.iris.db.tables.remote.Inflatable")):
            return obj.inflate(self.__wrapped__.getProcessorConnection())
        elif isinstance(obj, jpy.get_type("com.illumon.iris.db.tables.remote.ExportedTableDescriptorMessage")):
            return obj.inflate(self.__wrapped__.getProcessorConnection())
        elif isinstance(obj, jpy.get_type("com.illumon.iris.db.util.PythonRemoteQuery$PickledResult")):
            return dill.loads(base64.b64decode(obj.getPickled()))
        else:
            return obj

class AuthenticationManagerClass(type):
    classMap = {}

    def __getattr__(cls, name):
        if cls not in AuthenticationManagerClass.classMap:
            jtype = jpy.get_type("com.fishlib.auth.WAuthenticationClientManager")
            AuthenticationManagerClass.classMap[cls] = jtype
            x = jtype
        else:
            x = AuthenticationManagerClass.classMap[cls]
        return x.__dict__[name]

class AuthenticationManager:
    __metaclass__ = AuthenticationManagerClass


class FigureUnsupported():
    def __init__(self):
        raise Exception("Can not create a plot outside of the console.")

def __initializer__(jtype, obj):
    for key,value in jtype.__dict__.items():
        obj.__dict__.update({key : value})


def wrap_db(type, obj):
    return DbWrapper(obj)

def RemoteQueryClient(*args):
    jtype = jpy.get_type("com.illumon.iris.db.tables.remotequery.RemoteQueryClient")
    numargs = len(args)
    if numargs == 0:
        return jtype()
    elif numargs == 0:
        return jtype()
    elif numargs == 1:
        return jtype(args[0])
    elif numargs == 2:
        return jtype(args[0], args[1])
    else:
        return jtype(args[0], args[1], args[2])

def PythonRemoteQuery(dilledObject):
    jtype = jpy.get_type("com.illumon.iris.db.util.PythonRemoteQuery")
    return jtype(dilledObject)

def PythonRemoteQueryPickledResult(pickled):
    jtype = jpy.get_type("com.illumon.iris.db.util.PythonRemoteQuery$PickledResult")
    return jtype(pickled)

def PythonPushClassQuery(name, dilledObject):
    jtype = jpy.get_type("com.illumon.iris.db.util.PythonPushClassQuery")
    return jtype(name, dilledObject)

def PythonEvalQuery(string):
    jtype = jpy.get_type("com.illumon.iris.db.util.PythonEvalQuery")
    return jtype(string)

def RemoteDatabase(processorConnection):
    jtype = jpy.get_type("com.illumon.iris.db.tables.remote.RemoteDatabase")
    return jtype(processorConnection)

def Inflatable():
    jtype = jpy.get_type("com.illumon.iris.db.tables.remote.Inflatable")
    return jtype

def ExportedTableDescriptorMessage(id):
    jtype = jpy.get_type("com.illumon.iris.db.tables.remote.ExportedTableDescriptorMessage")
    return jtype(id)

def DistinctFormatter():
    jtype = jpy.get_type("com.illumon.iris.db.util.DBColorUtilImpl$DistinctFormatter")
    return jtype

def Config():
    return jpy.get_type("com.fishlib.configuration.Configuration").getInstance()

Figure = None
PlottingConvenience = None
def initialize():
    __initializer__(jpy.get_type("com.fishlib.configuration.Configuration"), Config)
    __initializer__(jpy.get_type("com.illumon.iris.db.tables.remotequery.RemoteQueryClient"), RemoteQueryClient)
    __initializer__(jpy.get_type("com.illumon.iris.db.util.PythonRemoteQuery"), PythonRemoteQuery)
    __initializer__(jpy.get_type("com.illumon.iris.db.util.PythonRemoteQuery$PickledResult"), PythonRemoteQueryPickledResult)
    __initializer__(jpy.get_type("com.illumon.iris.db.util.PythonPushClassQuery"), PythonPushClassQuery)
    __initializer__(jpy.get_type("com.illumon.iris.db.util.PythonEvalQuery"), PythonEvalQuery)
    __initializer__(jpy.get_type("com.illumon.iris.db.tables.remote.RemoteDatabase"), RemoteDatabase)
    __initializer__(jpy.get_type("com.illumon.iris.db.tables.remote.Inflatable"), Inflatable)
    __initializer__(jpy.get_type("com.illumon.iris.db.tables.remote.ExportedTableDescriptorMessage"), ExportedTableDescriptorMessage)
    __initializer__(jpy.get_type("com.illumon.iris.db.util.DBColorUtilImpl$DistinctFormatter"), DistinctFormatter)

    global Figure
    Figure = FigureUnsupported
    global PlottingConvenience
    PlottingConvenience = FigureUnsupported

    jpy.type_translations['com.illumon.iris.db.tables.remote.RemoteDatabase'] = wrap_db