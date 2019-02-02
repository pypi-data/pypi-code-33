import modelx as mx


m, s = mx.new_model(), mx.new_space()



defun = \
"""
def foo():
    print(x)
"""
ns = {}
lns = {'x':1}
def temp():
    exec(defun, ns, lns)

temp()