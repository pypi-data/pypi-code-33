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


class CreateDerivedTransactionPortfolioRequest(Model):
    """CreateDerivedTransactionPortfolioRequest.

    :param display_name: Portfolio display name
    :type display_name: str
    :param description: A long form text description of  the portfolio
    :type description: str
    :param code:
    :type code: str
    :param parent_portfolio_id:
    :type parent_portfolio_id: ~lusidtr.models.ResourceId
    :param created: The original creation date, defaults to today if not
     specified when creating a portfolio
    :type created: datetime
    :param corporate_action_source_id: Unique identifier for the corporate
     action source
    :type corporate_action_source_id: ~lusidtr.models.ResourceId
    :param accounting_method: Default taxlot selection method for the
     portfolio. Possible values include: 'Default', 'AverageCost',
     'FirstInFirstOut', 'LastInFirstOut', 'HighestCostFirst', 'LowestCostFirst'
    :type accounting_method: str or ~lusidtr.models.enum
    :param sub_holding_keys: Set of unique holding identifiers, e.g. trader,
     desk, strategy.
    :type sub_holding_keys: list[str]
    """

    _validation = {
        'display_name': {'required': True},
    }

    _attribute_map = {
        'display_name': {'key': 'displayName', 'type': 'str'},
        'description': {'key': 'description', 'type': 'str'},
        'code': {'key': 'code', 'type': 'str'},
        'parent_portfolio_id': {'key': 'parentPortfolioId', 'type': 'ResourceId'},
        'created': {'key': 'created', 'type': 'iso-8601'},
        'corporate_action_source_id': {'key': 'corporateActionSourceId', 'type': 'ResourceId'},
        'accounting_method': {'key': 'accountingMethod', 'type': 'str'},
        'sub_holding_keys': {'key': 'subHoldingKeys', 'type': '[str]'},
    }

    def __init__(self, display_name, description=None, code=None, parent_portfolio_id=None, created=None, corporate_action_source_id=None, accounting_method=None, sub_holding_keys=None):
        super(CreateDerivedTransactionPortfolioRequest, self).__init__()
        self.display_name = display_name
        self.description = description
        self.code = code
        self.parent_portfolio_id = parent_portfolio_id
        self.created = created
        self.corporate_action_source_id = corporate_action_source_id
        self.accounting_method = accounting_method
        self.sub_holding_keys = sub_holding_keys
