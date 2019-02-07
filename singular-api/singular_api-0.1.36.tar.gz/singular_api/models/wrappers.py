def inside_lib(func):
    def func_wrapper(*args, **kwargs):
        self = args[0]
        if self.__dict__.get('_BaseModel__initiated', False):
            return func(*args, *kwargs)
        before = self._BaseModel__inside_lib
        self._BaseModel__inside_lib = True
        ret = func(*args, **kwargs)
        self._BaseModel__inside_lib = before
        return ret
    return func_wrapper
