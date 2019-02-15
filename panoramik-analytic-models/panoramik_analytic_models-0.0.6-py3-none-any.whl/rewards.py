from infi.clickhouse_orm import fields, engines

from .fields import DateField, DateTimeField, JsonStringField, BoolStringField, StringField
from .db import CLUSTER_NAME, Model, DistributedModel


class RewardApplied(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    reward_id = StringField()
    source = StringField()
    reward_type = StringField()
    count = fields.UInt64Field()
    friend = StringField()
    extra = JsonStringField()
    autoclaim = BoolStringField()
    reward_created_on = StringField()
    accepted = BoolStringField()
    id = StringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'profile_id'))


class RewardAppliedDist(RewardApplied, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)
