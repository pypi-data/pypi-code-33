from functools import reduce
from typing import Any, List, Union, Tuple, Callable


def pipeline(value: Any, operations: List[Union[Tuple, Callable]]):
    def eval_s_expression(expression):
        if isinstance(expression, tuple):
            func, *args = expression

            def evaluate(x):
                return func(*args, x)
        else:

            def evaluate(x):
                return expression(x)

        return evaluate

    return reduce(lambda x, y: eval_s_expression(y)(x), operations, value)
