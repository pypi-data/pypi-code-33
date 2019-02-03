class FKLFunction:
    def __init__(self,function):
        self._function=function
        self._function_name=function.__name__
    def __call__(self,*arg):
        result=self._function(*arg)
        return result
    def GetFunctionName(self):
        return self._function_name

class FKLFunctionPool:
    def __init__(self):
        self._function_dict={}
    def __getitem__(self,function_name):
        if(type(function_name)!=str):
            raise Exception("FKLFunctionPool __getitem__ Error: The arg function_name must be str.")
        return self._function_dict[function_name]
    def Push(self,function):
        fkl_function=FKLFunction(function)
        function_name=fkl_function.GetFunctionName()
        if(self._function_dict.get(function_name,False)!=False):
            raise Exception("FKLFunctionPool Push Error: The function '{0}' already exist.".format(function_name))
        self._function_dict[function_name]=fkl_function
        return
    def Del(self,function_name):
        if(self._function_dict.get(function_name,False)!=False):
            del self._function_dict[function_name]
        return 
