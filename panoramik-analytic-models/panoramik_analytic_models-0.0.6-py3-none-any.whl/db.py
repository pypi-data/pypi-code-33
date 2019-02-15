import os
import re

from infi.clickhouse_orm import models
from infi.clickhouse_orm.fields import NullableField


camelcase_re = re.compile(r'([A-Z]+)(?=[a-z0-9])')

CLUSTER_NAME = os.environ.get('CLICKHOUSE_CLUSTER', 'anal')


def escape_none_values(cls, **kwargs):
    return {
        kwarg: escape_none_value(value, cls.get_field(kwarg))
        for kwarg, value in kwargs.items()
    }


def escape_none_value(value, field_cls):
    return field_cls.default \
        if value is None and not isinstance(field_cls, NullableField) else value


class Model(models.Model):
    def __init__(self, **kwargs):
        super(Model, self).__init__(**escape_none_values(self, **kwargs))

    def __setattr__(self, name, value):
        value = escape_none_value(value, self.get_field(name))
        super(Model, self).__setattr__(name, value)

    @classmethod
    def table_name(cls):
        def _join(match):
            word = match.group()

            if len(word) > 1:
                return ('_%s_%s' % (word[:-1], word[-1])).lower()

            return '_' + word.lower()

        return camelcase_re.sub(_join, cls.__name__).lstrip('_')

    def to_kafka_dict(self, include_readonly=True, field_names=None, exclude=None):
        fields = self.fields(writable=not include_readonly)

        if field_names is None:
            field_names = [f for f in fields]
        if exclude is None:
            exclude = []

        if field_names is not None:
            fields = [(n, f) for n, f in fields.items() if n in field_names and n not in exclude]

        data = self.__dict__
        kafka_dict = {}
        for name, field in fields:
            if hasattr(field, 'to_kafka'):
                kafka_dict[name] = field.to_kafka(data[name])
            else:
                kafka_dict[name] = data[name]
        return kafka_dict


class DistributedModel(Model, models.DistributedModel):
    pass
