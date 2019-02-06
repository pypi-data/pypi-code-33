class FKLFunctionPool:
    def __init__(self):
        self._function_dict={}
        pass
    def __getitem__(self,function_name):
        function=self._function_dict.get(function_name,None)
        if(function==None):
            raise Exception("FKLFunctionPool __getitem__ Error: The function is not in pool.")
        return function
    def Push(self,function):
        try:
            function_name=function.__name__
            self._function_dict[function_name]=function
        except:
            raise Exception("FKLFunctionPool Push Error: The input arg must be function.")
        return 
    def Del(self,function_name):
        function=self._function_dict.get(function_name,None)
        if(function==None):
            raise Exception("FKLFunctionPool Del Error: The function is not in pool.")
        del self._function_dict[function_name]
        return 
    