# coding=utf-8
# --------------------------------------------------------------------------
# # License
#
# Copyright &copy; 2018 FINBOURNE TECHNOLOGY LTD
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class PortfolioHolding(Model):
    """PortfolioHolding.

    :param instrument_uid: Id of the underlying security
    :type instrument_uid: str
    :param sub_holding_keys:
    :type sub_holding_keys: list[~lusidtr.models.PerpetualProperty]
    :param properties:
    :type properties: list[~lusidtr.models.Property]
    :param holding_type: Position type indicator of the holding
    :type holding_type: str
    :param units: Total number of units in the holding
    :type units: float
    :param settled_units: Total number of settled units in the holding
    :type settled_units: float
    :param cost: Total cost of the holding
    :type cost: ~lusidtr.models.CurrencyAndAmount
    :param cost_portfolio_ccy: Total cost of the holding
    :type cost_portfolio_ccy: ~lusidtr.models.CurrencyAndAmount
    :param transaction: Transaction behind a commitment-type holding
    :type transaction: ~lusidtr.models.Transaction
    """

    _validation = {
        'instrument_uid': {'required': True},
        'holding_type': {'required': True},
        'units': {'required': True},
        'settled_units': {'required': True},
        'cost': {'required': True},
        'cost_portfolio_ccy': {'required': True},
    }

    _attribute_map = {
        'instrument_uid': {'key': 'instrumentUid', 'type': 'str'},
        'sub_holding_keys': {'key': 'subHoldingKeys', 'type': '[PerpetualProperty]'},
        'properties': {'key': 'properties', 'type': '[Property]'},
        'holding_type': {'key': 'holdingType', 'type': 'str'},
        'units': {'key': 'units', 'type': 'float'},
        'settled_units': {'key': 'settledUnits', 'type': 'float'},
        'cost': {'key': 'cost', 'type': 'CurrencyAndAmount'},
        'cost_portfolio_ccy': {'key': 'costPortfolioCcy', 'type': 'CurrencyAndAmount'},
        'transaction': {'key': 'transaction', 'type': 'Transaction'},
    }

    def __init__(self, instrument_uid, holding_type, units, settled_units, cost, cost_portfolio_ccy, sub_holding_keys=None, properties=None, transaction=None):
        super(PortfolioHolding, self).__init__()
        self.instrument_uid = instrument_uid
        self.sub_holding_keys = sub_holding_keys
        self.properties = properties
        self.holding_type = holding_type
        self.units = units
        self.settled_units = settled_units
        self.cost = cost
        self.cost_portfolio_ccy = cost_portfolio_ccy
        self.transaction = transaction
