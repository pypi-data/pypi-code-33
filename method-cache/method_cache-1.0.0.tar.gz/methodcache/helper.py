


class WrapperFunction:

    def __init__(self, func):
        """
            Wrapps an given function/method

            :param func: "raw" function
        """
        self._hash = hash(func)
        self._func = func

    def get_hash(self):
        """
            Get hash of function
            :return string: Numeric Hash
        """
        return str(self._hash)

    def get_func(self):
        """
            Return given function
            :return func: "raw" function
        """
        return self._func

    def get_name(self):
        """
            Return Name of function
            :return str: Name of given function
        """
        return str(self._func.__name__)


class WrapperParameters:

    def __init__(self, arguments=(), keyword_arguments={}):
        """
            Wrap Parameters (arguments/args and keyword_arguments/kwargs) and provide a compared list of these two

            :param arguments: tuple of args
            :param keyword_arguments: dict of kwargs
        """
        self._args = list(arguments)
        self._kwargs = dict(keyword_arguments)

    def get_args(self):
        """
            Return list of given args
            :return list: args
        """
        return self._args

    def santize_args(self):
        """
            Create a dict from args. Every dict key start with the word "arg" followed by the value index of tuple.
            The value of this key are hashed
            :return dict: arguments as dict
        """
        param = {}
        for index, arg in enumerate(self._args):
            print(index)
            param["arg{}".format(index)] = hash(arg)
        return param

    def get_kwargs(self):
        """
            Return list of given kwargs
            :return list: kwargs
        """
        return self._kwargs

    def santize_kwargs(self):
        """
            Return a dict wich every value are hashed
            :return dict: kwargs with hashed values
        """
        param = {}
        for name, value in self._kwargs.items():
            try:
                param[name] = hash(value)
            except TypeError as e:
                param[name] = hash(tuple(sorted(hash(x) for x in value.items())))

        return param



    def santize_parameters(self):
        """
            Give a common list of args and kwargs. see santize_args and santize_kwargs
            :return dict: Merged dict of args and kwargs
        """
        return {**self.santize_args(), **self.santize_kwargs()}


