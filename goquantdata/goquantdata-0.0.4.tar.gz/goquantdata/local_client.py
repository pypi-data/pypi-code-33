import functools
import goquantdata

import quandl
import jqdatasdk

class LocalClient(object):
    def __init__(self, db_dir,
                 key_quandl=None,
                 key_alpha_vantage=None,
                 jq_password=None,
                 jq_username=None):

        self.db_dir = db_dir
        self.key_quandl = key_quandl
        self.key_alpha_vantage = key_alpha_vantage
        self.jq_username = jq_username
        self.jq_password = jq_password

        # copy all function from original jqdatasdk sdk
        for name in jqdatasdk.__dict__:  # iterate through every module's attributes
            val = jqdatasdk.__dict__[name]
            if callable(val):  # check if callable (normally functions)
                self.__dict__["jq_"+name] = val

        # copy all function from original quandl sdk
        for name in quandl.__dict__:  # iterate through every module's attributes
            val = quandl.__dict__[name]
            if callable(val):  # check if callable (normally functions)
                self.__dict__["ql_"+name] = val
        quandl.ApiConfig.api_key = self.key_quandl
        jqdatasdk.auth(jq_username, jq_password)


from .local.db.build_db import build_db
from .local.db.read_db import get_price, get_value


def make_api_method(func):
    """
    Provides a single entry point for modifying all API methods.
    For now this is limited to allowing the client object to be modified
    with an `extra_params` keyword arg to each method, that is then used
    as the params for each web service request.
    Please note that this is an unsupported feature for advanced use only.
    It's also currently incompatibile with multiple threads, see GH #160.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args[0]._extra_params = kwargs.pop("extra_params", None)
        result = func(*args, **kwargs)
        try:
            del args[0]._extra_params
        except AttributeError:
            pass
        return result
    return wrapper

LocalClient.build_db = make_api_method(build_db)
LocalClient.get_price = make_api_method(get_price)
LocalClient.get_value = make_api_method(get_value)
