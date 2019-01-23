import json

import boto3

from multiqq.adapters import BaseQueueAdapter


class AWSQueueAdapter(BaseQueueAdapter):
    """AWS SNS/SQS Adapter

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).

    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.

    Attributes:
        attr1 (str): Description of `attr1`.
        attr2 (:obj:`int`, optional): Description of `attr2`.

    """

    def __init__(self, consume_from_prefix=None, publish_to_prefix=None):
        self.consume_from_prefix = consume_from_prefix
        self.publish_to_prefix = publish_to_prefix
        self.sns = boto3.client('sns')
        self.sqs = boto3.client('sqs')

    def publish(self, channel, data):
        return self.sns.publish(TopicArn='%s%s' % (self.publish_to_prefix, channel), Message=json.dumps(data)).get('MessageId')

    def consume(self, channel, timeout=None):
        pass


if __name__ == '__main__':
    print('lalala')
    r = AWSQueueAdapter(publish_to_prefix='arn:aws:sns:us-west-2:218817830640:dev-')
    print(r.publish('generic-client', {'a': 'b'}))
