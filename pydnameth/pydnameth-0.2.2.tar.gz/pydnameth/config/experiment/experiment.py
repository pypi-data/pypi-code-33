"""
All levels can use only predefined enums
"""


class Experiment:

    def __init__(self,
                 type,
                 task,
                 method,
                 params,
                 ):
        self.type = type
        self.task = task
        self.method = method
        self.params = params

    def __str__(self):
        return self.get_experiment_str()

    def get_experiment_str(self):
        name = f'{self.type.value}_{self.task.value}_{self.method.value}'
        return name

    def get_params_str(self):
        name = ''
        if bool(self.params):
            params_keys = list(self.params.keys())
            if len(params_keys) > 0:
                params_keys.sort()
                name += '_'.join([key + '(' + str(self.params[key]) + ')' for key in params_keys])

        if name == '':
            name = 'default'

        return name

