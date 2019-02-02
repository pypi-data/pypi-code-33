

import modelx as mx

m, s = mx.new_model(), mx.new_space()

@mx.defcells
def fibo(n):
    if n == 0 or n == 1:
        return n
    else:
        return fibo(n-1) + fibo(n-2)

fibo(3)

node = fibo.preds(3)[0]

# node._baseattrs
#
# def print_preds(node, n):
#     for pred in node.preds:
#         print(n, pred)
#         print_preds(pred, n+1)
#