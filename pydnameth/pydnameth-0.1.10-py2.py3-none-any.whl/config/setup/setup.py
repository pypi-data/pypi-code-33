"""
All levels can use only predefined enums
"""


class Setup:

    def __init__(self,
                 experiment,
                 task,
                 method,
                 params,
                 ):
        self.experiment = experiment
        self.task = task
        self.method = method
        self.params = params

    def __str__(self):
        path = self.experiment.value + '/' + \
               self.task.value + '/' + \
               self.method.value
        return path

    def get_file_name(self):
        fn = ''
        if bool(self.params):
            params_keys = list(self.params.keys())
            if len(params_keys) > 0:
                params_keys.sort()
                fn += '_'.join([key + '(' + str(self.params[key]) + ')'
                                for key in params_keys])

        if fn == '':
            fn = 'default'

        return fn


__all__ = ['Setup']
