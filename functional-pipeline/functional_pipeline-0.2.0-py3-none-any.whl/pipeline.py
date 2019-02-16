from functools import reduce
from typing import Any, List, Union, Tuple, Callable


def pipeline(value: Any, operations: List[Union[Tuple, Callable]]):
    """
    Main Pipeline function.

    Takes a starting point `value` and a list of operations.
    An operation can be a function, or a tuple.

    If the operation is a function, it takes the value from the previous step in
    the pipeline and applies that argument to the function.

    If the operation is a tuple, the first argument is the function, and the rest of the
    tuple are arguments to apply in order.
    """

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
