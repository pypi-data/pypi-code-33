from . import skill_cmd
import numpy as np


"""
accellerated interface
"""

def decode_fn(name, catchfun):
    return lambda *args, **kwargs: catchfun(name,*args,**kwargs)


def pass_fun(name, self):
    return lambda *args, **kwargs: getattr(skill_cmd,name)(self.pyspectre,*args,**kwargs)


class Accelerated_scl_interface(object):

    functions_to_accel = [
        'getanalysis', 'getcircuit', 'getinstance', 'getmodel',
        'getprimitive', 'getpid', 'listmodel', 'getparameter',
        'listanalysis', 'listattribute', 'listcircuit', 'listinstance',
        'listnet', 'listparameter', 'listprimitive',
        'resolve',
    ]

    functions_to_ignore = ['findall']

    def __init__(self, pyspectre_inst):
        self.pyspectre = pyspectre_inst
        self.mem = {}
        self.sclobjs = {}

        if 'functions_to_accel' not in dir(self):
            self.functions_to_accel = []

        for name in dir(skill_cmd):
            if name not in dir(self) and name not in self.functions_to_ignore:
                obj = getattr(skill_cmd, name)
                if callable(obj):
                    if name not in self.functions_to_accel:
                        if name.startswith('isscl'):
                            setattr(self, name, obj)
                        else:
                            setattr(self, name, pass_fun(name, self))
                    else:
                        setattr(self, name, decode_fn(name, self.catchfun))

    # def wrap(self, func, *args, **kwargs):
    #     def tempfun(*args, **kwargs):
    #         return self.catchfun(func, *args, **kwargs)()
    #     return tempfun()

    def catchfun(self, fnname, *args, **kwargs):
        allargs = list(args) + list(zip(kwargs.items()))
        try:
            r = self.mem[fnname]
            if allargs:
                for item in allargs:
                    r = r[item]
                return r
            else:
                return r['__none__']

        except:
            bare_fn = getattr(skill_cmd, fnname)
            result = bare_fn(self.pyspectre, *args, **kwargs)
            if fnname not in self.mem:
                self.mem.update({fnname: {}})
            if allargs:
                r = {allargs[-1]: result}
                if len(allargs)>1:
                    for item in allargs[:-1].reverse():
                        r.update({item: r})
                self.mem[fnname].update({list(r.keys())[0]:list(r.values())[0]})
            else:
                self.mem[fnname].update({'__none__':result})
            return result


    """
    High-level SCL functions
    """


    """
    Mid-level SCL functions
    """

    """list functions"""

    def listattribute(self, obj, child=None):
        if child:
            return skill_cmd.listattribute(self.pyspectre, self.resolve( obj, child))
        else:
            return skill_cmd.listattribute(self.pyspectre, self.resolve( obj))

    def listparams(self, obj):
        return skill_cmd.listparameter(self.pyspectre, self.resolve(obj))

    """get functions"""

    def getanalparams(self, list_of_params):
        return {name: self.getparametervalue(self.pyspectre.analysis_name, param) for name in list_of_params}

    def getcircuit(self, obj):
        obj = self.resolve( obj)
        if self.issclckt(obj):
            return obj
        else:
            return None

    def getparameter(self, obj, paramname):
        obj = self.resolve(obj)
        return skill_cmd.getparameter(self.pyspectre, obj, paramname)

    def getparametervalue(self, obj, paramname):
        obj = self.resolve(obj)
        p = self.getparameter( obj, paramname)
        return self.getattribute( p, "value")

    """ SET FUNCTIONS"""

    def setparametervalue(self, obj, param, val, block=True):
        # availparams = self.listparameter(self, obj)
        # if param not in availparams:
        #     raise LookupError('can\'t find specified parameter:{!r} for object: {|r}:'.format(param,obj))
        sclobj = self.resolve(obj)
        paramobj = self.resolve(sclobj, param)
        paramattrs = self.listattribute(paramobj)

        if paramattrs["datatype"] == 'scalar enumerated':
            paramattrs["range"] = ''.join(paramattrs["range"].split()).split(',')
            if val not in paramattrs["range"]:
                raise IOError(
                    'can\'t find specified value:{!r} in enumerated-type parameter: {!r}'.format(val, param)
                )

        elif paramattrs["datatype"] == 'scalar string' and isinstance(val, (float, int)):
            val = '\"{}\"'.format(val)

        elif paramattrs["datatype"] == 'vector real pair':
            if isinstance(val, (list, tuple, np.ndarray)):
                val = '[{}]'.format(' '.join(['{:e}'.format(item) for item in val]))
            elif isinstance(val, str):
                assert val.startswith('[') and val.endswith(']')

        try:
            paramobj = self.getparameter(sclobj, param)
            result = self.setattribute(paramobj, "value", val, block=block)
            return result

        except Exception as e:
            print("failed on parameter named: {} for instance: {}".format(param, obj))
            raise e

    def runanalysis(self, analysis, block=True):
        self.setresultdir(self.pyspectre.results_dir)
        skill_cmd.runanalysis(self.pyspectre, self.resolve(analysis), block=block)
        # self.setresultdir('psf')
        return

    def resolve(self, desc, child=None):
        if not child:
            if desc in self.sclobjs:
                return self.sclobjs[desc]['addr']
            elif self.issclobj(desc):
                p = desc
            else:
                try:
                    p = self.getanalysis(desc)
                except LookupError:
                    try:
                        p = self.getinstance(desc)
                        # p = self.getcircuit(desc)
                    except LookupError:
                        try:
                            p = self.getparameter( skill_cmd.getcircuit(self.pyspectre,''), desc)
                        except LookupError:
                            try:
                                p = skill_cmd.getcircuit(self.pyspectre, desc)
                                # p = self.getinstance(desc)
                            except LookupError:
                                expanded = desc.split('.')
                                p, c = expanded[0], expanded[1:]
                                try:
                                    p = self.resolve(p, child=c)
                                except:
                                    raise LookupError('couldn\'t resolve \"{}\"'.format(desc))

            self.sclobjs.update({desc: {'addr': p, 'sub': {}}})
            return p

        elif child:

            p = self.resolve(desc)

            if child in self.sclobjs[desc]['sub']:
                return self.sclobjs[desc]['sub'][child]
            else:
                if self.issclobj(child):
                    c = child
                else:
                    try:
                        c = self.getparameter(p, child)
                        # c = self.getattribute(p, child)
                    except LookupError:
                        try:
                            c = self.getattribute(p, child)
                            # c = self.getparameter(p, child)
                        except LookupError:
                            raise LookupError('couldn\'t resolve \"{}.{}\"'.format(desc, child))

            self.sclobjs[desc]['sub'].update({child: c})
            return c

