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


class TransactionConfigurationData(Model):
    """TransactionConfigurationData.

    :param aliases: Representative movements for transaction code
    :type aliases: list[~lusidtr.models.TransactionConfigurationTypeAlias]
    :param movements: Representative movements for transaction code
    :type movements:
     list[~lusidtr.models.TransactionConfigurationMovementData]
    :param properties:
    :type properties: list[~lusidtr.models.PerpetualProperty]
    """

    _validation = {
        'aliases': {'required': True},
        'movements': {'required': True},
    }

    _attribute_map = {
        'aliases': {'key': 'aliases', 'type': '[TransactionConfigurationTypeAlias]'},
        'movements': {'key': 'movements', 'type': '[TransactionConfigurationMovementData]'},
        'properties': {'key': 'properties', 'type': '[PerpetualProperty]'},
    }

    def __init__(self, aliases, movements, properties=None):
        super(TransactionConfigurationData, self).__init__()
        self.aliases = aliases
        self.movements = movements
        self.properties = properties
