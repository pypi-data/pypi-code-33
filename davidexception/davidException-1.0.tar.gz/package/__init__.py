from .validates import validate_value, tiny_int
from .error import TinyIntError

def tiny_int_eval(val):
    try:
        if validate_value(val) and tiny_int(val):
            return True
        else:
            raise TinyIntError()
    except TinyIntError as error:
        print(error)
