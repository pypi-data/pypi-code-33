from methodcache.store import Store
from methodcache.helper import WrapperFunction, WrapperParameters
from methodcache.exceptions import NoMethod, TTLExpired
import logging
# Decorator Args

logging.basicConfig(level=logging.DEBUG)


def cache(**options):
    """
        Decorator method for caching

        :param ttl: Time to life for this Cache Entry in Seconds
        :param store: Storage Object. To this object the cache entry was saved
        :param category: String in which Category the cache object should be sorted
    """

    def funcwrapper(func):
        """
            Decorator Wrapper

            :param func: Orginal Funciton
            :return: Modifed Function
        """

        def methodcall(*args, **kwargs):
            """
                Cache Implementaiton Checks if method in same category with the same
                :param args: Handover Arguments from orginal method
                :param kwargs: Handover KeywordArguemnts from Orginal Method
                :return:
            """

            _func = WrapperFunction(func)
            _params = WrapperParameters(args, kwargs)

            return add_to_cache(options, _func, _params)

        return methodcall

    return funcwrapper


def add_to_cache(options={}, func=None, params=None):
    """
        Seperated Add To Cache Method; Contains the function stack to add a function and there result to cache

        :param options: dict with keys of store,category,ttl (previously validated)
        :param func: orginal function
        :param params: WrapperParameters object with *args and **kwargs from orginal function
        :return any: Result created by orignal function
    """
    #: Contains validated options
    cleaned_options = {}

    #: Check Store; Create Store as static attribute in Store class or use handover store argument
    if "store" not in options:
        setattr(Store, "_default_store", Store())
        cleaned_options["store"] = getattr(Store, "_default_store")
    else:
        assert isinstance(options["store"], Store)
        cleaned_options["store"] = options["store"]

    #: Check TTL; Set TTL from Store object or use handover argument ttl argument
    if "ttl" not in options:

        assert type(cleaned_options["store"].ttl) is int
        cleaned_options["ttl"] = cleaned_options["store"].ttl

    else:
        assert type(options["ttl"]) is int
        cleaned_options["ttl"] = options["ttl"]

    #: Check category; Set default category or check if string
    if "category" not in options:
        cleaned_options["category"] = "default"
    else:
        assert type(options["category"]) is str
        cleaned_options["category"] = options["category"]

    assert func is not None
    assert isinstance(params, WrapperParameters)
    assert isinstance(func, WrapperFunction)

    method_store = cleaned_options["store"].get_method_store(*cleaned_options["category"].split(":"))

    try:
        meth_obj = method_store.get_method(func, params)
        return meth_obj.get_result()
    except NoMethod as e:
        result = func.get_func()(*params.get_args(), **params.get_kwargs())
        method_store.create(func, params, result)
        return result
    except TTLExpired as e:
        result = func.get_func()(*params.get_args(), **params.get_kwargs())
        method_store.create(func, params, result)
        return result
