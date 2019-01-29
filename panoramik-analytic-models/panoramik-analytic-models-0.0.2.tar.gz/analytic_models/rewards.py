from infi.clickhouse_orm import fields, engines

from .fields import DateField, DateTimeField, JsonStringField, BoolStringField
from .db import CLUSTER_NAME, Model, DistributedModel


class RewardApplied(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    reward_id = fields.StringField()
    source = fields.StringField()
    reward_type = fields.StringField()
    count = fields.UInt64Field()
    friend = fields.StringField()
    extra = JsonStringField()
    autoclaim = BoolStringField()
    reward_created_on = fields.StringField()
    accepted = BoolStringField()
    id = fields.StringField()

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class RewardAppliedDist(RewardApplied, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class Rewards(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    action = fields.StringField()
    custom_id = fields.StringField()
    reward_type = fields.StringField()
    reward_id = fields.StringField()
    source = fields.StringField()
    count = fields.UInt64Field()
    friend = fields.StringField()
    extra = JsonStringField()
    autoclaim = BoolStringField()

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class RewardsDist(Rewards, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


