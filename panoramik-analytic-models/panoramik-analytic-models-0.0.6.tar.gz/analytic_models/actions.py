from infi.clickhouse_orm import engines, fields

from .fields import DateField, DateTimeField, StringField, JsonStringField
from .db import CLUSTER_NAME, Model, DistributedModel


# TODO deprecated
class ActionLog(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    character_id = StringField(default='1')
    action_id = StringField()
    parent_id = StringField()
    top_parent_id = StringField()
    action_name = StringField()
    action_details = JsonStringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'top_parent_id'))


class ActionLogDist(ActionLog, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


# TODO create table
class InGameLocationChanges(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    character_id = StringField(default='1')
    location = StringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'profile_id'))


class InGameLocationChangesDist(InGameLocationChanges, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


# TODO create table
class LevelInfoChanges(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    rank = fields.UInt64Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'profile_id'))


class LevelInfoChangesDist(LevelInfoChanges, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


# TODO create table
class TutorialSteps(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    step = fields.UInt64Field()
    env = StringField()
    player_country = StringField()
    platform_id = StringField()
    version = StringField()
    os_version = StringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'step'))


class TutorialStepsDist(TutorialSteps, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


# TODO create table
class UsersLoggedIn(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    name = StringField()
    rank = fields.UInt64Field()
    league = fields.UInt64Field(default=32)
    guild_id = fields.UInt64Field()
    register_date = DateTimeField()
    platform_id = StringField()
    origin_id = StringField()
    user_timezone = StringField()
    user_language = StringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'profile_id'))


class UsersLoggedInDist(UsersLoggedIn, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)
