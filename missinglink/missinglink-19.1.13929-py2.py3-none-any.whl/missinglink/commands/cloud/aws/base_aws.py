import boto3
import six


class AwsBase(object):
    def __init__(self, aws_ctx, org):
        self.ctx = aws_ctx
        self.org = org

    @classmethod
    def client(cls, name, aws_ctx):
        return boto3.client(name, region_name=aws_ctx.region)

    @classmethod
    def resource(cls, name, aws_ctx):
        return boto3.resource(name, region_name=aws_ctx.region)

    @classmethod
    def dict_to_tuple_array(cls, data, key='Key', value='Value', value_transformer=None):
        def default_transformation(x):
            return x

        if value_transformer is None:
            value_transformer = default_transformation
        return [{key: k, value: value_transformer(v)} for k, v in data.items()]

    @classmethod
    def tuple_array_do_dict(cls, data, key='Key', value='Value'):
        return {x[key]: x[value] for x in data}

    @classmethod
    def ensure_str(cls, value):
        if isinstance(value, bytes):
            return value.decode('utf-8')

        if isinstance(value, six.string_types):
            return value

        if value is None:
            return ''

        return str(value)
