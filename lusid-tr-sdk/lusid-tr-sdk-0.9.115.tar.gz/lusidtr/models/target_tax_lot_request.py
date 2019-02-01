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


class TargetTaxLotRequest(Model):
    """TargetTaxLotRequest.

    :param units:
    :type units: float
    :param cost:
    :type cost: ~lusidtr.models.CurrencyAndAmount
    :param portfolio_cost:
    :type portfolio_cost: float
    :param price:
    :type price: float
    :param purchase_date:
    :type purchase_date: datetime
    :param settlement_date:
    :type settlement_date: datetime
    """

    _validation = {
        'units': {'required': True},
    }

    _attribute_map = {
        'units': {'key': 'units', 'type': 'float'},
        'cost': {'key': 'cost', 'type': 'CurrencyAndAmount'},
        'portfolio_cost': {'key': 'portfolioCost', 'type': 'float'},
        'price': {'key': 'price', 'type': 'float'},
        'purchase_date': {'key': 'purchaseDate', 'type': 'iso-8601'},
        'settlement_date': {'key': 'settlementDate', 'type': 'iso-8601'},
    }

    def __init__(self, units, cost=None, portfolio_cost=None, price=None, purchase_date=None, settlement_date=None):
        super(TargetTaxLotRequest, self).__init__()
        self.units = units
        self.cost = cost
        self.portfolio_cost = portfolio_cost
        self.price = price
        self.purchase_date = purchase_date
        self.settlement_date = settlement_date
