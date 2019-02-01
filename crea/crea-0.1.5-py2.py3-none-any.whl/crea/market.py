# This Python file uses the following encoding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str
import random
import pytz
import logging
from datetime import datetime, timedelta
from crea.instance import shared_crea_instance
from .utils import (
    formatTimeFromNow, formatTime, formatTimeString, assets_from_string, parse_time, addTzInfo)
from .asset import Asset
from .amount import Amount
from .price import Price, Order, FilledOrder
from .account import Account
from creabase import operations
from creagraphenebase.py23 import bytes_types, integer_types, string_types, text_type
REQUEST_MODULE = None
if not REQUEST_MODULE:
    try:
        import requests
        REQUEST_MODULE = "requests"
    except ImportError:
        REQUEST_MODULE = None
log = logging.getLogger(__name__)


class Market(dict):
    """ This class allows to easily access Markets on the blockchain for trading, etc.

        :param Crea crea_instance: Crea instance
        :param Asset base: Base asset
        :param Asset quote: Quote asset
        :returns: Blockchain Market
        :rtype: dictionary with overloaded methods

        Instances of this class are dictionaries that come with additional
        methods (see below) that allow dealing with a market and its
        corresponding functions.

        This class tries to identify **two** assets as provided in the
        parameters in one of the following forms:

        * ``base`` and ``quote`` are valid assets (according to :class:`crea.asset.Asset`)
        * ``base:quote`` separated with ``:``
        * ``base/quote`` separated with ``/``
        * ``base-quote`` separated with ``-``

        .. note:: Throughout this library, the ``quote`` symbol will be
                  presented first (e.g. ``CREA:CBD`` with ``CREA`` being the
                  quote), while the ``base`` only refers to a secondary asset
                  for a trade. This means, if you call
                  :func:`crea.market.Market.sell` or
                  :func:`crea.market.Market.buy`, you will sell/buy **only
                  quote** and obtain/pay **only base**.

    """

    def __init__(
        self,
        base=None,
        quote=None,
        crea_instance=None,
    ):
        """
        Init Market

            :param crea.crea.Crea crea_instance: Crea instance
            :param crea.asset.Asset base: Base asset
            :param crea.asset.Asset quote: Quote asset
        """
        self.crea = crea_instance or shared_crea_instance()

        if quote is None and isinstance(base, str):
            quote_symbol, base_symbol = assets_from_string(base)
            quote = Asset(quote_symbol, crea_instance=self.crea)
            base = Asset(base_symbol, crea_instance=self.crea)
            super(Market, self).__init__({"base": base, "quote": quote})
        elif base and quote:
            quote = Asset(quote, crea_instance=self.crea)
            base = Asset(base, crea_instance=self.crea)
            super(Market, self).__init__({"base": base, "quote": quote})
        elif base is None and quote is None:
            quote = Asset("CBD", crea_instance=self.crea)
            base = Asset("CREA", crea_instance=self.crea)
            super(Market, self).__init__({"base": base, "quote": quote})
        else:
            raise ValueError("Unknown Market config")

    def get_string(self, separator=":"):
        """ Return a formated string that identifies the market, e.g. ``CREA:CBD``

            :param str separator: The separator of the assets (defaults to ``:``)
        """
        return "%s%s%s" % (self["quote"]["symbol"], separator, self["base"]["symbol"])

    def __eq__(self, other):
        if isinstance(other, str):
            quote_symbol, base_symbol = assets_from_string(other)
            return (
                self["quote"]["symbol"] == quote_symbol and
                self["base"]["symbol"] == base_symbol
            ) or (
                self["quote"]["symbol"] == base_symbol and
                self["base"]["symbol"] == quote_symbol
            )
        elif isinstance(other, Market):
            return (
                self["quote"]["symbol"] == other["quote"]["symbol"] and
                self["base"]["symbol"] == other["base"]["symbol"]
            )

    def ticker(self, raw_data=False):
        """ Returns the ticker for all markets.

            Output Parameters:

            * ``latest``: Price of the order last filled
            * ``lowest_ask``: Price of the lowest ask
            * ``highest_bid``: Price of the highest bid
            * ``sbd_volume``: Volume of CBD
            * ``crea_volume``: Volume of CREA
            * ``percent_change``: 24h change percentage (in %)

            .. note::
                Market is CREA:CBD and prices are CBD per CREA!

            Sample Output:

            .. code-block:: js

                 {
                    'highest_bid': 0.30100226633322913,
                    'latest': 0.0,
                    'lowest_ask': 0.3249636958897082,
                    'percent_change': 0.0,
                    'sbd_volume': 108329611.0,
                    'crea_volume': 355094043.0
                }

        """
        data = {}
        # Core Exchange rate
        self.crea.rpc.set_next_node_on_empty_reply(True)
        ticker = self.crea.rpc.get_ticker(api="market_history")

        if raw_data:
            return ticker

        data["highest_bid"] = Price(
            ticker["highest_bid"],
            base=self["base"],
            quote=self["quote"],
            crea_instance=self.crea
        )
        data["latest"] = Price(
            ticker["latest"],
            quote=self["quote"],
            base=self["base"],
            crea_instance=self.crea
        )
        data["lowest_ask"] = Price(
            ticker["lowest_ask"],
            base=self["base"],
            quote=self["quote"],
            crea_instance=self.crea
        )
        data["percent_change"] = float(ticker["percent_change"])
        data["sbd_volume"] = Amount(ticker["sbd_volume"], crea_instance=self.crea)
        data["crea_volume"] = Amount(ticker["crea_volume"], crea_instance=self.crea)

        return data

    def volume24h(self, raw_data=False):
        """ Returns the 24-hour volume for all markets, plus totals for primary currencies.

            Sample output:

            .. code-block:: js

                {
                    "CREA": 361666.63617,
                    "CBD": 1087.0
                }

        """
        self.crea.rpc.set_next_node_on_empty_reply(True)
        volume = self.crea.rpc.get_volume(api="market_history")
        if raw_data:
            return volume
        return {
            self["base"]["symbol"]: Amount(volume["sbd_volume"], crea_instance=self.crea),
            self["quote"]["symbol"]: Amount(volume["crea_volume"], crea_instance=self.crea)
        }

    def orderbook(self, limit=25, raw_data=False):
        """ Returns the order book for CBD/CREA market.

            :param int limit: Limit the amount of orders (default: 25)

            Sample output (raw_data=False):

                .. code-block:: none

                    {
                        'asks': [
                            380.510 CREA 460.291 CBD @ 1.209669 CBD/CREA,
                            53.785 CREA 65.063 CBD @ 1.209687 CBD/CREA
                        ],
                        'bids': [
                            0.292 CREA 0.353 CBD @ 1.208904 CBD/CREA,
                            8.498 CREA 10.262 CBD @ 1.207578 CBD/CREA
                        ],
                        'asks_date': [
                            datetime.datetime(2018, 4, 30, 21, 7, 24, tzinfo=<UTC>),
                            datetime.datetime(2018, 4, 30, 18, 12, 18, tzinfo=<UTC>)
                        ],
                        'bids_date': [
                            datetime.datetime(2018, 4, 30, 21, 1, 21, tzinfo=<UTC>),
                            datetime.datetime(2018, 4, 30, 20, 38, 21, tzinfo=<UTC>)
                        ]
                    }

            Sample output (raw_data=True):

                .. code-block:: js

                    {
                        'asks': [
                            {
                                'order_price': {'base': '8.000 CREA', 'quote': '9.618 CBD'},
                                'real_price': '1.20225000000000004',
                                'crea': 4565,
                                'sbd': 5488,
                                'created': '2018-04-30T21:12:45'
                            }
                        ],
                        'bids': [
                            {
                                'order_price': {'base': '10.000 CBD', 'quote': '8.333 CREA'},
                                'real_price': '1.20004800192007677',
                                'crea': 8333,
                                'sbd': 10000,
                                'created': '2018-04-30T20:29:33'
                            }
                        ]
                    }

            .. note:: Each bid is an instance of
                class:`crea.price.Order` and thus carries the keys
                ``base``, ``quote`` and ``price``. From those you can
                obtain the actual amounts for sale

        """
        self.crea.rpc.set_next_node_on_empty_reply(True)
        if self.crea.rpc.get_use_appbase():
            orders = self.crea.rpc.get_order_book({'limit': limit}, api="market_history")
        else:
            orders = self.crea.rpc.get_order_book(limit, api='database_api')
        if raw_data:
            return orders
        asks = list([Order(
            Amount(x["order_price"]["quote"], crea_instance=self.crea),
            Amount(x["order_price"]["base"], crea_instance=self.crea),
            crea_instance=self.crea) for x in orders["asks"]])
        bids = list([Order(
            Amount(x["order_price"]["quote"], crea_instance=self.crea),
            Amount(x["order_price"]["base"], crea_instance=self.crea),
            crea_instance=self.crea).invert() for x in orders["bids"]])
        asks_date = list([formatTimeString(x["created"]) for x in orders["asks"]])
        bids_date = list([formatTimeString(x["created"]) for x in orders["bids"]])
        data = {"asks": asks, "bids": bids, "asks_date": asks_date, "bids_date": bids_date}
        return data

    def recent_trades(self, limit=25, raw_data=False):
        """ Returns the order book for a given market. You may also
            specify "all" to get the orderbooks of all markets.

            :param int limit: Limit the amount of orders (default: 25)
            :param bool raw_data: when False, FilledOrder objects will be
                returned

            Sample output (raw_data=False):

                .. code-block:: none

                    [
                        (2018-04-30 21:00:54+00:00) 0.267 CREA 0.323 CBD @ 1.209738 CBD/CREA,
                        (2018-04-30 20:59:30+00:00) 0.131 CREA 0.159 CBD @ 1.213740 CBD/CREA,
                        (2018-04-30 20:55:45+00:00) 0.093 CREA 0.113 CBD @ 1.215054 CBD/CREA,
                        (2018-04-30 20:55:30+00:00) 26.501 CREA 32.058 CBD @ 1.209690 CBD/CREA,
                        (2018-04-30 20:55:18+00:00) 2.108 CREA 2.550 CBD @ 1.209677 CBD/CREA,
                    ]

            Sample output (raw_data=True):

                .. code-block:: js

                    [
                        {'date': '2018-04-30T21:02:45', 'current_pays': '0.235 CBD', 'open_pays': '0.194 CREA'},
                        {'date': '2018-04-30T21:02:03', 'current_pays': '24.494 CBD', 'open_pays': '20.248 CREA'},
                        {'date': '2018-04-30T20:48:30', 'current_pays': '175.464 CREA', 'open_pays': '211.955 CBD'},
                        {'date': '2018-04-30T20:48:30', 'current_pays': '0.999 CREA', 'open_pays': '1.207 CBD'},
                        {'date': '2018-04-30T20:47:54', 'current_pays': '0.273 CBD', 'open_pays': '0.225 CREA'},
                    ]

            .. note:: Each bid is an instance of
                :class:`crea.price.Order` and thus carries the keys
                ``base``, ``quote`` and ``price``. From those you can
                obtain the actual amounts for sale

        """
        self.crea.rpc.set_next_node_on_empty_reply(limit > 0)
        if self.crea.rpc.get_use_appbase():
            orders = self.crea.rpc.get_recent_trades({'limit': limit}, api="market_history")['trades']
        else:
            orders = self.crea.rpc.get_recent_trades(limit, api="market_history")
        if raw_data:
            return orders
        filled_order = list([FilledOrder(x, crea_instance=self.crea) for x in orders])
        return filled_order

    def trade_history(self, start=None, stop=None, intervall=None, limit=25, raw_data=False):
        """ Returns the trade history for the internal market

            This function allows to fetch a fixed number of trades at fixed
            intervall times to reduce the call duration time. E.g. it is possible to
            receive the trades from the last 7 days, by fetching 100 trades each 6 hours.

            When intervall is set to None, all trades are received between start and stop.
            This can take a while.

            :param datetime start: Start date
            :param datetime stop: Stop date
            :param timedelta intervall: Defines the intervall
            :param int limit: Defines how many trades are fetched at each intervall point
            :param bool raw_data: when True, the raw data are returned
        """
        utc = pytz.timezone('UTC')
        if not stop:
            stop = utc.localize(datetime.utcnow())
        if not start:
            start = stop - timedelta(hours=1)
        start = addTzInfo(start)
        stop = addTzInfo(stop)
        current_start = start
        filled_order = []
        fo = self.trades(start=current_start, stop=stop, limit=limit, raw_data=raw_data)
        if intervall is None and len(fo) > 0:
            current_start = fo[-1]["date"]
            filled_order += fo
        elif intervall is not None:
            current_start += intervall
            filled_order += [fo]
        last_date = fo[-1]["date"]
        while (len(fo) > 0 and last_date < stop):
            fo = self.trades(start=current_start, stop=stop, limit=limit, raw_data=raw_data)
            if len(fo) == 0 or fo[-1]["date"] == last_date:
                break
            last_date = fo[-1]["date"]
            if intervall is None:
                current_start = last_date
                filled_order += fo
            else:
                current_start += intervall
                filled_order += [fo]
        return filled_order

    def trades(self, limit=100, start=None, stop=None, raw_data=False):
        """ Returns your trade history for a given market.

            :param int limit: Limit the amount of orders (default: 100)
            :param datetime start: start time
            :param datetime stop: stop time

        """
        # FIXME, this call should also return whether it was a buy or
        # sell
        utc = pytz.timezone('UTC')
        if not stop:
            stop = utc.localize(datetime.utcnow())
        if not start:
            start = stop - timedelta(hours=24)
        start = addTzInfo(start)
        stop = addTzInfo(stop)
        self.crea.rpc.set_next_node_on_empty_reply(False)
        if self.crea.rpc.get_use_appbase():
            orders = self.crea.rpc.get_trade_history({'start': formatTimeString(start),
                                                       'end': formatTimeString(stop),
                                                       'limit': limit}, api="market_history")['trades']
        else:
            orders = self.crea.rpc.get_trade_history(
                formatTimeString(start),
                formatTimeString(stop),
                limit, api="market_history")
        if raw_data:
            return orders
        filled_order = list([FilledOrder(x, crea_instance=self.crea) for x in orders])
        return filled_order

    def market_history_buckets(self):
        self.crea.rpc.set_next_node_on_empty_reply(True)
        ret = self.crea.rpc.get_market_history_buckets(api="market_history")
        if self.crea.rpc.get_use_appbase():
            return ret['bucket_sizes']
        else:
            return ret

    def market_history(self, bucket_seconds=300, start_age=3600, end_age=0, raw_data=False):
        """ Return the market history (filled orders).

            :param int bucket_seconds: Bucket size in seconds (see
                `returnMarketHistoryBuckets()`)
            :param int start_age: Age (in seconds) of the start of the
                window (default: 1h/3600)
            :param int end_age: Age (in seconds) of the end of the window
                (default: now/0)
            :param bool raw_data: (optional) returns raw data if set True

            Example:

                .. code-block:: js

                    {
                        'close_sbd': 2493387,
                        'close_crea': 7743431,
                        'high_sbd': 1943872,
                        'high_crea': 5999610,
                        'id': '7.1.5252',
                        'low_sbd': 534928,
                        'low_crea': 1661266,
                        'open': '2016-07-08T11:25:00',
                        'open_sbd': 534928,
                        'open_crea': 1661266,
                        'sbd_volume': 9714435,
                        'seconds': 300,
                        'crea_volume': 30088443
                    }

        """
        buckets = self.market_history_buckets()
        if bucket_seconds < 5 and bucket_seconds >= 0:
            bucket_seconds = buckets[bucket_seconds]
        else:
            if bucket_seconds not in buckets:
                raise ValueError("You need select the bucket_seconds from " + str(buckets))
        self.crea.rpc.set_next_node_on_empty_reply(False)
        if self.crea.rpc.get_use_appbase():
            history = self.crea.rpc.get_market_history({'bucket_seconds': bucket_seconds,
                                                         'start': formatTimeFromNow(-start_age - end_age),
                                                         'end': formatTimeFromNow(-end_age)}, api="market_history")['buckets']
        else:
            history = self.crea.rpc.get_market_history(
                bucket_seconds,
                formatTimeFromNow(-start_age - end_age),
                formatTimeFromNow(-end_age),
                api="market_history")
        if raw_data:
            return history
        new_history = []
        for h in history:
            if 'open' in h and isinstance(h.get('open'), string_types):
                h['open'] = formatTimeString(h.get('open', "1970-01-01T00:00:00"))
            new_history.append(h)
        return new_history

    def accountopenorders(self, account=None, raw_data=False):
        """ Returns open Orders

            :param Account account: Account name or instance of Account to show orders for in this market
            :param bool raw_data: (optional) returns raw data if set True,
                or a list of Order() instances if False (defaults to False)
        """
        if not account:
            if "default_account" in self.crea.config:
                account = self.crea.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, full=True, crea_instance=self.crea)

        r = []
        # orders = account["limit_orders"]
        if not self.crea.is_connected():
            return None
        self.crea.rpc.set_next_node_on_empty_reply(False)
        if self.crea.rpc.get_use_appbase():
            orders = self.crea.rpc.find_limit_orders({'account': account["name"]}, api="database")['orders']
        else:
            orders = self.crea.rpc.get_open_orders(account["name"])
        if raw_data:
            return orders
        for o in orders:
            order = {}
            order["order"] = Order(
                Amount(o["sell_price"]["base"], crea_instance=self.crea),
                Amount(o["sell_price"]["quote"], crea_instance=self.crea),
                crea_instance=self.crea
            )
            order["orderid"] = o["orderid"]
            order["created"] = formatTimeString(o["created"])
            r.append(order)
        return r

    def buy(
        self,
        price,
        amount,
        expiration=None,
        killfill=False,
        account=None,
        orderid=None,
        returnOrderId=False
    ):
        """ Places a buy order in a given market

            :param float price: price denoted in ``base``/``quote``
            :param number amount: Amount of ``quote`` to buy
            :param number expiration: (optional) expiration time of the order in seconds (defaults to 7 days)
            :param bool killfill: flag that indicates if the order shall be killed if it is not filled (defaults to False)
            :param string account: Account name that executes that order
            :param string returnOrderId: If set to "head" or "irreversible" the call will wait for the tx to appear in
                the head/irreversible block and add the key "orderid" to the tx output

            Prices/Rates are denoted in 'base', i.e. the CBD_CREA market
            is priced in CREA per CBD.

            **Example:** in the CBD_CREA market, a price of 300 means
            a CBD is worth 300 CREA

            .. note::

                All prices returned are in the **reversed** orientation as the
                market. I.e. in the CREA/CBD market, prices are CBD per CREA.
                That way you can multiply prices with `1.05` to get a +5%.

            .. warning::

                Since buy orders are placed as
                limit-sell orders for the base asset,
                you may end up obtaining more of the
                buy asset than you placed the order
                for. Example:

                    * You place and order to buy 10 CBD for 100 CREA/CBD
                    * This means that you actually place a sell order for 1000 CREA in order to obtain **at least** 10 CBD
                    * If an order on the market exists that sells CBD for cheaper, you will end up with more than 10 CBD
        """
        if not expiration:
            expiration = self.crea.config["order-expiration"]
        if not account:
            if "default_account" in self.crea.config:
                account = self.crea.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, crea_instance=self.crea)

        if isinstance(price, Price):
            price = price.as_base(self["base"]["symbol"])

        if isinstance(amount, Amount):
            amount = Amount(amount, crea_instance=self.crea)
            if not amount["asset"]["symbol"] == self["quote"]["symbol"]:
                raise AssertionError("Price: {} does not match amount: {}".format(
                    str(price), str(amount)))
        elif isinstance(amount, str):
            amount = Amount(amount, crea_instance=self.crea)
        else:
            amount = Amount(amount, self["quote"]["symbol"], crea_instance=self.crea)

        order = operations.Limit_order_create(**{
            "owner": account["name"],
            "orderid": orderid or random.getrandbits(32),
            "amount_to_sell": Amount(
                float(amount) * float(price),
                self["base"]["symbol"],
                crea_instance=self.crea
            ),
            "min_to_receive": Amount(
                float(amount),
                self["quote"]["symbol"],
                crea_instance=self.crea
            ),
            "expiration": formatTimeFromNow(expiration),
            "fill_or_kill": killfill,
            "prefix": self.crea.prefix,
        })

        if returnOrderId:
            # Make blocking broadcasts
            prevblocking = self.crea.blocking
            self.crea.blocking = returnOrderId

        tx = self.crea.finalizeOp(order, account["name"], "active")

        if returnOrderId:
            tx["orderid"] = tx["operation_results"][0][1]
            self.crea.blocking = prevblocking

        return tx

    def sell(
        self,
        price,
        amount,
        expiration=None,
        killfill=False,
        account=None,
        orderid=None,
        returnOrderId=False
    ):
        """ Places a sell order in a given market

            :param float price: price denoted in ``base``/``quote``
            :param number amount: Amount of ``quote`` to sell
            :param number expiration: (optional) expiration time of the order in seconds (defaults to 7 days)
            :param bool killfill: flag that indicates if the order shall be killed if it is not filled (defaults to False)
            :param string account: Account name that executes that order
            :param string returnOrderId: If set to "head" or "irreversible" the call will wait for the tx to appear in
                the head/irreversible block and add the key "orderid" to the tx output

            Prices/Rates are denoted in 'base', i.e. the CBD_CREA market
            is priced in CREA per CBD.

            **Example:** in the CBD_CREA market, a price of 300 means
            a CBD is worth 300 CREA

            .. note::

                All prices returned are in the **reversed** orientation as the
                market. I.e. in the CREA/CBD market, prices are CBD per CREA.
                That way you can multiply prices with `1.05` to get a +5%.
        """
        if not expiration:
            expiration = self.crea.config["order-expiration"]
        if not account:
            if "default_account" in self.crea.config:
                account = self.crea.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, crea_instance=self.crea)
        if isinstance(price, Price):
            price = price.as_base(self["base"]["symbol"])

        if isinstance(amount, Amount):
            amount = Amount(amount, crea_instance=self.crea)
            if not amount["asset"]["symbol"] == self["quote"]["symbol"]:
                raise AssertionError("Price: {} does not match amount: {}".format(
                    str(price), str(amount)))
        elif isinstance(amount, str):
            amount = Amount(amount, crea_instance=self.crea)
        else:
            amount = Amount(amount, self["quote"]["symbol"], crea_instance=self.crea)

        order = operations.Limit_order_create(**{
            "owner": account["name"],
            "orderid": orderid or random.getrandbits(32),
            "amount_to_sell": Amount(
                float(amount),
                self["quote"]["symbol"],
                crea_instance=self.crea
            ),
            "min_to_receive": Amount(
                float(amount) * float(price),
                self["base"]["symbol"],
                crea_instance=self.crea
            ),
            "expiration": formatTimeFromNow(expiration),
            "fill_or_kill": killfill,
            "prefix": self.crea.prefix,
        })
        if returnOrderId:
            # Make blocking broadcasts
            prevblocking = self.crea.blocking
            self.crea.blocking = returnOrderId

        tx = self.crea.finalizeOp(order, account["name"], "active")

        if returnOrderId:
            tx["orderid"] = tx["operation_results"][0][1]
            self.crea.blocking = prevblocking

        return tx

    def cancel(self, orderNumbers, account=None, **kwargs):
        """ Cancels an order you have placed in a given market. Requires
            only the "orderNumbers".

            :param orderNumbers: A single order number or a list of order numbers
            :type orderNumbers: int, list
        """
        if not account:
            if "default_account" in self.crea.config:
                account = self.crea.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, full=False, crea_instance=self.crea)

        if not isinstance(orderNumbers, (list, set, tuple)):
            orderNumbers = {orderNumbers}

        op = []
        for order in orderNumbers:
            op.append(
                operations.Limit_order_cancel(**{
                    "owner": account["name"],
                    "orderid": order,
                    "prefix": self.crea.prefix}))
        return self.crea.finalizeOp(op, account["name"], "active", **kwargs)

    @staticmethod
    def _weighted_average(values, weights):
        """ Calculates a weighted average
        """
        if not (len(values) == len(weights) and len(weights) > 0):
            raise AssertionError("Length of both array must be the same and greater than zero!")
        return sum(x * y for x, y in zip(values, weights)) / sum(weights)

    @staticmethod
    def btc_usd_ticker(verbose=False):
        """ Returns the BTC/USD price from bitfinex, gdax, kraken, okcoin and bitstamp. The mean price is
            weighted by the exchange volume.
        """
        prices = {}
        responses = []
        urls = [
            "https://api.bitfinex.com/v1/pubticker/BTCUSD",
            "https://api.gdax.com/products/BTC-USD/ticker",
            "https://api.kraken.com/0/public/Ticker?pair=XBTUSD",
            "https://www.okcoin.com/api/v1/ticker.do?symbol=btc_usd",
            "https://www.bitstamp.net/api/v2/ticker/btcusd/",
        ]
        try:
            responses = list(requests.get(u, timeout=30) for u in urls)
        except Exception as e:
            log.debug(str(e))

        for r in [x for x in responses
                  if hasattr(x, "status_code") and x.status_code == 200 and x.json()]:
            try:
                if "bitfinex" in r.url:
                    data = r.json()
                    prices['bitfinex'] = {
                        'price': float(data['last_price']),
                        'volume': float(data['volume'])}
                elif "gdax" in r.url:
                    data = r.json()
                    prices['gdax'] = {
                        'price': float(data['price']),
                        'volume': float(data['volume'])}
                elif "kraken" in r.url:
                    data = r.json()['result']['XXBTZUSD']['p']
                    prices['kraken'] = {
                        'price': float(data[0]),
                        'volume': float(data[1])}
                elif "okcoin" in r.url:
                    data = r.json()["ticker"]
                    prices['okcoin'] = {
                        'price': float(data['last']),
                        'volume': float(data['vol'])}
                elif "bitstamp" in r.url:
                    data = r.json()
                    prices['bitstamp'] = {
                        'price': float(data['last']),
                        'volume': float(data['volume'])}
            except KeyError as e:
                log.info(str(e))

        if verbose:
            print(prices)

        if len(prices) == 0:
            raise RuntimeError("Obtaining BTC/USD prices has failed from all sources.")

        # vwap
        return Market._weighted_average(
            [x['price'] for x in prices.values()],
            [x['volume'] for x in prices.values()])

    @staticmethod
    def crea_btc_ticker():
        """ Returns the CREA/BTC price from bittrex, binance, huobi and upbit. The mean price is
            weighted by the exchange volume.
        """
        prices = {}
        responses = []
        urls = [
            # "https://poloniex.com/public?command=returnTicker",
            "https://bittrex.com/api/v1.1/public/getmarketsummary?market=BTC-CREA",
            "https://api.binance.com/api/v1/ticker/24hr",
            "https://api.huobi.pro/market/history/kline?period=1day&size=1&symbol=creabtc",
            "https://crix-api.upbit.com/v1/crix/trades/ticks?code=CRIX.UPBIT.BTC-CREA&count=1",
        ]
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'}
        try:
            responses = list(requests.get(u, headers=headers, timeout=30) for u in urls)
        except Exception as e:
            log.debug(str(e))

        for r in [x for x in responses
                  if hasattr(x, "status_code") and x.status_code == 200 and x.json()]:
            try:
                if "poloniex" in r.url:
                    data = r.json()["BTC_CREA"]
                    prices['poloniex'] = {
                        'price': float(data['last']),
                        'volume': float(data['baseVolume'])}
                elif "bittrex" in r.url:
                    data = r.json()["result"][0]
                    price = (data['Bid'] + data['Ask']) / 2
                    prices['bittrex'] = {'price': price, 'volume': data['BaseVolume']}
                elif "binance" in r.url:
                    data = [x for x in r.json() if x['symbol'] == 'CREABTC'][0]
                    prices['binance'] = {
                        'price': float(data['lastPrice']),
                        'volume': float(data['quoteVolume'])}
                elif "huobi" in r.url:
                    data = r.json()["data"][-1]
                    prices['huobi'] = {
                        'price': float(data['close']),
                        'volume': float(data['vol'])}
                elif "upbit" in r.url:
                    data = r.json()[-1]
                    prices['upbit'] = {
                        'price': float(data['tradePrice']),
                        'volume': float(data['tradeVolume'])}
            except KeyError as e:
                log.info(str(e))

        if len(prices) == 0:
            raise RuntimeError("Obtaining CREA/BTC prices has failed from all sources.")

        return Market._weighted_average(
            [x['price'] for x in prices.values()],
            [x['volume'] for x in prices.values()])

    def crea_usd_implied(self):
        """Returns the current CREA/USD market price"""
        return self.crea_btc_ticker() * self.btc_usd_ticker()
