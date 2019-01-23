import functools

class A(object):
    def __init__(self, func):
        self._func = func

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)


def get_func_signature(func, focus):
    '''
    focus(Int): position of arg to be focused
    '''
    arg_num = func.__code__.co_argcount
    sign = "%s(%s)"%(func.__name__, ','.join(func.__code__.co_varnames[:arg_num]))
    focus_spaces = len(func.__name__)
    focus_spaces += 1 # '('
    for a in func.__code__.co_varnames[:focus]:
        focus_spaces += len(a) + 1
    focus_line = ' '* focus_spaces + '^'
    return '%s\n%s'%(sign, focus_line)

class ArgTypeInvalid(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class check_args:
    def __init__(self, *types):
        self._types = types

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kargs):
            for a, t, i in zip(args, self._types, range(len(args))):
                if not isinstance(a, t):
                    raise ArgTypeInvalid("real arg type is %s, but %s is needed\n%s"%(type(a), t, get_func_signature(func, i)))
            return func(*args, **kargs)
        return wrapper




# print(test_func(1, 2, "nihao"))
# print(test_join("nihao", " beijing"))
# print(test_func(1, 3, "world"))
# print(test_join("hello", " beijing"))
