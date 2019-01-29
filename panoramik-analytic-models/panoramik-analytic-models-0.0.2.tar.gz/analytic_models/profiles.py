from infi.clickhouse_orm import fields, engines

from .fields import DateField, DateTimeField, JsonStringField, BoolStringField
from .db import CLUSTER_NAME, Model, DistributedModel


class ArmyCollectionLog(Model):
    day = DateField()
    profile_id = fields.StringField()
    created_on = DateTimeField()
    actions = JsonStringField()
    difference = JsonStringField()

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class ArmyCollectionLogDist(ArmyCollectionLog, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class CheaterMarks(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    is_paying = BoolStringField()
    action = fields.StringField()

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class CheaterMarksDist(CheaterMarks, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class Registers(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    env = fields.StringField()
    player_country = fields.StringField()
    utm_campaign = fields.StringField()
    utm_medium = fields.StringField()
    utm_source = fields.StringField()
    utm_full = fields.StringField()
    platform_id = fields.StringField()
    advertising_id = fields.StringField() # MP only

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class RegistersDist(Registers, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class ResourcesLog(Model):
    day = DateField()
    profile_id = fields.StringField()
    created_on = DateTimeField()
    actions = JsonStringField()
    difference = JsonStringField()

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class ResourcesLogDist(ResourcesLog, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class Sessions(Model):
    day = DateField()
    event_type = fields.StringField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    session_id = fields.StringField()
    env = fields.StringField()
    device_id = fields.StringField()
    player_country = fields.StringField()
    platform_id = fields.StringField()
    client_ip = fields.StringField()
    login_id = fields.StringField() # AP only
    request_id = fields.StringField() # AP only

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class SessionsDist(Sessions, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class TroopsHiding(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    guild_id = fields.UInt64Field()
    guild_name = fields.StringField()
    war_id = fields.UInt64Field()
    room_number = fields.UInt64Field()
    spent_gems = fields.UInt64Field()
    cell_x = fields.UInt64Field()
    cell_y = fields.UInt64Field()
    hidden = BoolStringField()

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class TroopsHidingDist(TroopsHiding, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)
