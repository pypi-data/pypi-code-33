from shioaji.base import BaseObj, attrs

__all__ = ('Contract Stock Option').split()


@attrs
class Contract(BaseObj):
    """ the base contract object

    Attributes:
        symbol (str): 
        security_type (str): {STK, FUT, OPT}
        currency (str): 
        exchange (str):
        code (str):
        name (str):
        category (str):
        delivery_month (str)
        strike_price (int or float):
        option_right (str): {C, P}
        underlying_kind (str):
        underlying_code (str)
        unit (int or float): 
        multiplier (int): 
    """
    _defaults = dict(
        symbol='',
        security_type='',
        currency='TWD',
        exchange='TAIFEX',
        code='',
        name='',
        category='',
        delivery_month='',
        strike_price=0,
        option_right='',
        underlying_kind='',
        underlying_code='',
        unit=0,
        multiplier=0,
    )

    def __init__(self, *args, **kwargs):
        BaseObj.__init__(self, *args, **kwargs)

    def astype(self):
        return _CONTRACTTYPE.get(self.security_type, self.__class__)(**self)


class Stock(Contract):
    _force_def = dict(security_type='STK')


class Future(Contract):
    _force_def = dict(security_type='FUT')


class Option(Contract):
    _force_def = dict(security_type='OPT')


_CONTRACTTYPE = {'STK': Stock, 'FUT': Future, 'OPT': Option}


@attrs
class Contracts(BaseObj):
    _defaults = dict(Stocks=None, Futures=None, Options=None)

    def __init__(self, *args, **kwargs):
        BaseObj.__init__(self, *args, **kwargs)
        self._Futures = FutureContracts(self.Futures)
        self._Options = OptionContracts(self.Options)


class OptionContracts:

    def __init__(self, contracts_dict):
        #resp = {}  #_list_futopt_code('O', True, client)
        self.__slots__ = [(key, setattr(self, key, MultiContract(key,
                                                                 value)))[0]
                          for key, value in contracts_dict.items()]

    def __repr__(self):
        return '({})'.format(', '.join(self.__slots__))


class FutureContracts:

    def __init__(self, contracts_dict):
        self.__slots__ = [(key, setattr(self, key, MultiContract(key,
                                                                 value)))[0]
                          for key, value in contracts_dict.items()]

    def __repr__(self):
        return '({})'.format(', '.join(self.__slots__))


class MultiContract:

    def __init__(self, name, contracts):
        self._name = name
        self.__slots__ = [(cont['symbol'],
                           setattr(self, cont['symbol'],
                                   Contract(**cont).astype()))[0]
                          for cont in contracts] + ['_name']

    def __repr__(self):
        return "{}({})".format(self._name, (', ').join(self.__slots__[:-1]))
