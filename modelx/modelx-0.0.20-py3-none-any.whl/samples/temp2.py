from modelx import *

model, space = new_model('ReprModel'), new_space('ReprSpace')


@defcells
def Foo(x, y):
    return x * y


def params(m):
    return None


model.new_space('DynSpace', formula=params)

model.DynSpace(1)