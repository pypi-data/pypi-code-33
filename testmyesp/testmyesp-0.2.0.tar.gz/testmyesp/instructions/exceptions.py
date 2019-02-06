
class InstructionException(Exception):
    pass


class NoSuchInstruction(InstructionException):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class InvalidInstructionParameters(InstructionException):
    def __init__(self, name, params):
        self.name = name
        self.params = params

    def __str__(self):
        params = ('{}={}'.format(k, v) for k, v in self.params.items())
        params_str = ', '.join(params)

        return '{}({})'.format(self.name, params_str)
