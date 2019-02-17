def plus(a, b):
    """
    Returns the sum of a and b.
    """
    return a + b


def minus(a, b):
    """
    Returns the difference between a and b.
    """
    return a - b


def times(a, b):
    """
    Returns the product of a and b.
    """
    return a * b


def divided_by(a, b):
    """
    Returns the ratio of a to b.
    """
    return a / b


def max_of(a, b):
    """
    Returns the larger of the values a and b.
    """
    if a >= b:
        return a
    return b


def max_in(values):
    """
    Returns the largest value in `values`,
     or `None` if the input list is empty.
    """
    max_value = None
    for v in values:
        if max_value is None or v > max_value:
            max_value = v
    return max_value


def main(*args):
    """
    Computes the result of applying two operands to an operator. The input to the
    function is expected to be of form <operator> <num1> <num2>.
    The possible values for the operators are 'add', 'subtract', 'multiply',
    and 'divide'. This function returns a tuple (success, message), where success
    is a boolean value indicating whether the function exited correctly.
    """
    operators = {
        "add": plus,
        "subtract": minus,
        "multiply": times,
        "divide": divided_by,
    }
    error = False

    try:
        operator = args[0]
        lhs = int(args[1])
        rhs = int(args[2])
    except (IndexError, ValueError):
        error = True

    if error or operator not in operators:
        return False, "Expected: yks <add|subtract|multiply|divide> <num1> <num2>."

    try:
        result = operators[operator](lhs, rhs)
    except ZeroDivisionError:
        return False, "Division by zero encountered."

    return True, str(result)


def console_run():
    """
    Calls the main function with system args.
    This function is meant to be called as an entrypoint script.
    """
    import sys

    success, message = main(*sys.argv[1:])
    print(message)
    sys.exit(0 if success else 1)
