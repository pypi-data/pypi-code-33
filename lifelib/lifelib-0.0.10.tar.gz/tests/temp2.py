import modelx as mx


m, s = mx.new_model(), mx.new_space()


@mx.defcells
def foo(x):
    return x

@mx.defcells
def bar(y):
    return y

@mx.defcells
def baz():
    return 3

for i in range(5):
    foo(i)
    bar(i)
    baz()

s.frame

