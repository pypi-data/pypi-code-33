import modelx as mx
from modelx import defcells

m = mx.new_model()

def no_values():

    model = mx.new_model('Model')
    space = model.new_space('Space')

    @defcells
    def param0():
        return 0

    @defcells
    def param1(x):
        return x

    @defcells
    def param2(x, y):
        return x * y

    return space

s = no_values()

s.param2.node(3, 4)