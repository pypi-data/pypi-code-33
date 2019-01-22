#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

import pickle
from sos.utils import short_repr, env

__init_statement__ = '''
def __version_info__(module):
    # return the version of Python module
    try:
        code = ("import %s; version=str(%s.__version__)" %
                (module, module))
        ns_g = ns_l = {}
        exec(compile(code, "<string>", "exec"), ns_g, ns_l)
        return ns_l["version"]
    except Exception as e:
        import pkg_resources
        try:
            return pkg_resources.require(module)[0].version
        except Exception as e:
            return 'na'


def __loaded_modules__():
    from types import ModuleType
    res = []
    for key,value in globals().items():
        if isinstance(value, ModuleType):
            res.append([value.__name__, __version_info__(value.__name__)])
    return [(x,y) for x,y in res if y != 'na']
'''


class sos_Python:
    supported_kernels = {'Python3': ['python3'], 'Python2': ['python2']}
    background_color = {'Python2': '#FFF177', 'Python3': '#FFD91A'}
    options = {
        'variable_pattern': r'^\s*[_A-Za-z0-9\.]+\s*$',
        'assignment_pattern': r'^\s*([_A-Za-z0-9\.]+)\s*=.*$'
    }
    cd_command = 'import os;os.chdir({dir!r})'

    def __init__(self, sos_kernel, kernel_name='python3'):
        self.sos_kernel = sos_kernel
        self.kernel_name = kernel_name
        self.init_statements = __init_statement__

    def get_vars(self, names):
        self.sos_kernel.run_cell("import pickle", True, False)
        for name in names:
            if self.kernel_name == 'python3':
                stmt = "globals().update(pickle.loads({!r}))\n".format(
                    pickle.dumps({name: env.sos_dict[name]}))
            else:
                stmt = "globals().update(pickle.loads({!r}))\n".format(
                    pickle.dumps({name: env.sos_dict[name]}, protocol=2, fix_imports=True))
            self.sos_kernel.run_cell(
                stmt,
                True, False, on_error='Failed to get variable {} from SoS to {}'.format(name, self.kernel_name))

    def load_pickled(self, item):
        if isinstance(item, bytes):
            return pickle.loads(item)
        elif isinstance(item, str):
            return pickle.loads(item.encode('utf-8'))
        else:
            self.sos_kernel.warn('Cannot restore from result of pickle.dumps: {}'.format(short_repr(item)))
            return {}

    def put_vars(self, items, to_kernel=None):
        stmt = 'import pickle\n__vars__={{ {} }}\n__vars__.update({{x:y for x,y in locals().items() if x.startswith("sos")}})\npickle.dumps(__vars__)'.format(
            ','.join('"{0}":{0}'.format(x) for x in items))
        try:
            # sometimes python2 kernel would fail to send a execute_result and lead to an error
            response = self.sos_kernel.get_response(
                stmt, ['execute_result'])[-1][1]
        except:
            return {}

        # Python3 -> Python3
        if (self.kernel_name == 'python3' and to_kernel == 'Python3') or \
                (self.kernel_name == 'python2' and to_kernel == 'Python2'):
            # to self, this should allow all variables to be passed
            return 'import pickle\nglobals().update(pickle.loads({}))'.format(response['data']['text/plain'])
        try:
            ret = self.load_pickled(eval(response['data']['text/plain']))
            if self.sos_kernel._debug_mode:
                self.sos_kernel.warn('Get: {}'.format(ret))
            return ret
        except Exception as e:
            self.sos_kernel.warn(
                'Failed to import variables {}: {}'.format(items, e))
            return {}

    def sessioninfo(self):
        modules = self.sos_kernel.get_response(
            'import pickle;import sys;res=[("Version", sys.version)];res.extend(__loaded_modules__());pickle.dumps(res)', ['execute_result'])[0][1]
        return self.load_pickled(eval(modules['data']['text/plain']))
