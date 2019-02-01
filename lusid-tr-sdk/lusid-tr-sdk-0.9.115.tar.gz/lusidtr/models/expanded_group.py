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


class ExpandedGroup(Model):
    """ExpandedGroup.

    :param href:
    :type href: str
    :param id:
    :type id: ~lusidtr.models.ResourceId
    :param name:
    :type name: str
    :param description:
    :type description: str
    :param values:
    :type values: list[~lusidtr.models.CompletePortfolio]
    :param sub_groups:
    :type sub_groups: list[~lusidtr.models.ExpandedGroup]
    :param version:
    :type version: ~lusidtr.models.Version
    :param links:
    :type links: list[~lusidtr.models.Link]
    """

    _attribute_map = {
        'href': {'key': 'href', 'type': 'str'},
        'id': {'key': 'id', 'type': 'ResourceId'},
        'name': {'key': 'name', 'type': 'str'},
        'description': {'key': 'description', 'type': 'str'},
        'values': {'key': 'values', 'type': '[CompletePortfolio]'},
        'sub_groups': {'key': 'subGroups', 'type': '[ExpandedGroup]'},
        'version': {'key': 'version', 'type': 'Version'},
        'links': {'key': 'links', 'type': '[Link]'},
    }

    def __init__(self, href=None, id=None, name=None, description=None, values=None, sub_groups=None, version=None, links=None):
        super(ExpandedGroup, self).__init__()
        self.href = href
        self.id = id
        self.name = name
        self.description = description
        self.values = values
        self.sub_groups = sub_groups
        self.version = version
        self.links = links
