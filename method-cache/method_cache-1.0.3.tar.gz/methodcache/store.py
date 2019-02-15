from methodcache.exceptions import NoMethod, TTLExpired
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class Store:

    def __init__(self, ttl=60):
        """
            This object stores the structured Cache Data
            :param ttl: Default Time to Live of an single cache data
        """
        self.ttl = ttl
        self._store = {}

    def get_method_store(self, *category):
        """
            Get the MethodStore from category/subcategory
            If no methodstore exists, create a new one

            :param category: list of category and thier subcategorys
            :return MethodStore: Return new or old MethodStore Object
        """
        category = self.get_category(*category, full=True)
        #: Return exsiting MethodStore
        if "method_store" in category:
            return category["method_store"]
        else:
            # Create new Empty methods dict
            category["method_store"] = MethodStore(self)
            return category["method_store"]

    def get_all_categorys(self):
        """
            List of all categories on root level

            :return:
        """
        category_list = list(self._store.keys())
        category_list.remove("method_store")
        return category_list

    def get_category(self, *category_tuple, full=False):
        """
            GoTo category level given in category_tuple and return this level content
            :param category_tuple: List of Categorys
            :param full: return the full cateogry not only the names
            :return:
        """
        #: Convert tuple to list
        category = list(category_tuple)

        def _helper(cache_store, cat_list):
            # Result Methods dict if empty
            if len(cat_list) <= 1:
                # Return existing methods dict
                return cache_store

            # Deattach next category name
            cur_cat = cat_list.pop(0)
            # resolve sub category "dict"
            if cur_cat in cache_store:
                return _helper(cache_store[cur_cat], cat_list)
            else:
                # Create new category "dict"
                cache_store[cur_cat] = {}
                return _helper(cache_store[cur_cat], cat_list)

        #: return full category level
        if full:
            return _helper(self._store, category)
        #: Return only the categorie names
        category_list = list(_helper(self._store, category).keys())
        category_list.remove("method_store")
        return category_list


class MethodStore:

    def __init__(self, store, *args, **kwargs):
        self._store = store
        self._method_list = {}

    def _get_func(self, func):
        """
            Method Serializer Method
            :param func: WrapperFunction
            :return string: A string that identifies the given function
        """
        return func.get_name()

    def has_method(self, func):
        """
            Check if function is stored in this MethodStore Object

            :param func: WrapperFunction with the searched funciton
            :return bool: True if method existes in this store
        """
        funcstr = self._get_func(func)
        if funcstr in self._method_list:
            return True
        return False

    def has_method_call(self, func, params):
        """
            Like has_method. This Checks also if a method with the given arguments exists

            :param func: WrapperFunction contains the function
            :param params: WrapperParameters contains arguments and keyword arguments
            :return bool: True if method call exists and stored in this MEthodStore
        """
        funcstr = self._get_func(func)

        if funcstr not in self._method_list:
            return False

        meth_obj_list = self._method_list[funcstr]

        for meth_obj in meth_obj_list:
            if meth_obj.has_params__exactly(params):
                return True

        return False

    def get_method(self, func, params):
        """
            Returns the MethodObject identified by func and params

            :param func: WrappedFunction Object to identifiy search method
            :param params: WrappedParameters Object to check if a object with this parameters is stored
            :return MethodObject: the MethodObject with the cache Information
        """
        funcstr = self._get_func(func)

        #: Raise If funcstring not in _method_list
        if funcstr not in self._method_list:
            raise NoMethod("No Method registerd with name {}".format(funcstr))

        meth_obj_list = self._method_list[funcstr]

        for meth_obj in meth_obj_list:
            if meth_obj.has_params__exactly(params):
                if datetime.now() > meth_obj.create_timestamp+timedelta(seconds=self._store.ttl):

                    index = self._method_list[funcstr].index(meth_obj)
                    self._method_list[funcstr].pop(index)

                    del meth_obj
                    raise TTLExpired("Cache Object is too old")

                return meth_obj

        raise NoMethod("No Method found with name {} and same parameters".format(funcstr))

    def create(self, func, params, result):
        """
        Create a new Cache Entry

        :param func: WrappedFunction for wich function the entry created
        :param params: WrappedParameter which parameters used to get this result
        :param result: string Result
        """
        funcstr = self._get_func(func)

        if funcstr not in self._method_list:
            self._method_list[funcstr] = []

        self._method_list[funcstr].append(MethodObject(func, params, result))


class MethodObject:

    def __init__(self, func, params, result):
        """
            Stores the Data of an Cache Entry. resp. this is the cache entry

            :param func: WrapperFunction of cached function
            :param params: WrapperParameter of function with called arguments of this function
            :param result: Function result
        """
        self._func = func
        self._params = params
        self._result = result
        self.create_timestamp = datetime.now()

    def get_result(self):
        return self._result

    def get_eta(self):
        return (self.create_timestamp + timedelta(seconds=self._store.ttl))-datetime.now()

    def has_params__exactly(self, params):
        """
            Check if the Parameters are excatly the same wich are given as argument
            :param params: WrapperParameters to compare
            :return bool: True if the params are the same
        """
        ext_params = params.santize_parameters()
        int_params = self._params.santize_parameters()

        if len(set(int_params) ^ set(ext_params)) <= 0:
            compare = True
            for paramname in ext_params:
                if not ext_params[paramname] == int_params[paramname]:
                    compare = False
            return compare
        else:
            return False

