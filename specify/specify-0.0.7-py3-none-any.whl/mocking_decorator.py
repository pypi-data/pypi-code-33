from prophepy import prophesize

def mock(cls):
    def func_wrapper(func):
        mocked_object = prophesize(cls)

        def arg_wrapper(*args):
            self = args[0]
            self._mocked_objects.append(mocked_object)
            return func(*args, mocked_object)

        return arg_wrapper

    return func_wrapper
