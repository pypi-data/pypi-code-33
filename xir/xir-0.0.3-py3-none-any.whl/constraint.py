
class Constraint(dict):
    def __init__(self, op, value):
        dict.__init__(self, constraint__=op, value__=value)

    def __str__(self):
        return self['constraint__']+ repr(self['value__'])

    def __repr__(self):
        return self['constraint__']+ repr(self['value__'])


def eq(value):
    return Constraint('=', value)

def lt(value):
    return Constraint('<', value)

def le(value):
    return Constraint('<=', value)


def gt(value):
    return Constraint('>', value)
def ge(value):
    return Constraint('>=', value)

def between(lower, upper):
    return Constraint('<>', [lower,upper])

def choice(value):
    return Constraint('?', value)
def select(value):
    return Constraint('[]', value)


