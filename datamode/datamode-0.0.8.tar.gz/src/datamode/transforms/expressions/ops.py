# Vectorized operations are WAY faster than running df.apply with axis=1, since these don't run in a loop (at least not Python)
# https://realpython.com/fast-flexible-pandas/
def apply_comparison_op(op, item1, item2):
  if op == '==':
    return item1 == item2

  elif op == '!=':
    return item1 != item2

  elif op == '<':
    return item1 < item2

  elif op == '<=':
    return item1 <= item2

  elif op == '>':
    return item1 > item2

  elif op == '>=':
    return item1 >= item2


def apply_math_op(op, item1, item2):
  if op == '+':
    return item1 + item2

  elif op == '-':
    return item1 - item2

  elif op == '*':
    return item1 * item2

  elif op == '/':
    return item1 / item2

  elif op == '**':
    return item1 ** item2
