# -*- coding:utf-8 -*-

import six
import re

__all__ = ['GridDimParseSerializeMixin', 'GridDimLUTMixin']


class GridDimParseSerializeMixin(object):
    """requires: name"""
    parser = None
    serializer = None

    def parse(self, value):
        if not self.parser:
            return value

        if callable(self.parser):
            return self.parser(value)

    def serialize(self, value):
        if not self.serializer:
            return u"{}".format(value)

        if callable(self.serializer):
            return self.serializer(value)
        elif isinstance(self.serializer, six.string_types):
            if re.match(r'.*{[^{}]*}.*', self.serializer):
                return self.serializer.format(value)
            elif '%' in self.serializer:
                return self.serializer % value
            else:
                raise ValueError("Invalid serializer in dim {}: {}".format(self.name, self.serializer))


class GridDimLUTMixin(object):
    """Requires: serialize, values"""
    _true_lut = None

    @property
    def _lut(self):
        if self._true_lut is None:
            return self._build_lut(self.values)
        else:
            return self._true_lut

    def _build_lut(self, values):
        return {self.serialize(v): i for i, v in enumerate(values)}


