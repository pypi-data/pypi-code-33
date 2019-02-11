#! -*- coding: utf-8 -*-

import decimal
import json

class JSONEncoder(json.JSONEncoder):
    """ Custom encode for json dumps

        To use a custom ``JSONEncoder`` subclass (e.g. one that overrides the
        ``.default()`` method to serialize additional types), specify it with
        the ``cls`` kwarg; otherwise ``JSONEncoder`` is used. """

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return super(JSONEncoder, self).default(obj)