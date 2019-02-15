from infi.clickhouse_orm import fields, engines

from .fields import DateField, DateTimeField, JsonStringField, BoolStringField, StringField
from .db import CLUSTER_NAME, Model, DistributedModel


class ArmyCollectionLog(Model):
    day = DateField()
    profile_id = StringField()
    created_on = DateTimeField()
    actions = JsonStringField()
    difference = JsonStringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'profile_id'))


class ArmyCollectionLogDist(ArmyCollectionLog, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class CheaterMarks(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    is_paying = BoolStringField()
    action = StringField()

    engine = engines.MergeTree(partition_key=('toYYYYMMDD(day)',), order_by=('profile_id',))


class CheaterMarksDist(CheaterMarks, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class ProfileDynamics(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    session_id = StringField()
    occurance_type = StringField()
    occurance_value = StringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'occurance_type'))


class ProfileDynamicsDist(ProfileDynamics, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class ProfileStatus(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    session_id = StringField()
    env = StringField()
    platform_id = StringField()
    player_country = StringField()
    install_timestamp = DateTimeField()
    appsflyer_id = StringField()
    is_paying = BoolStringField()
    is_cheater = BoolStringField()
    is_qa = BoolStringField()
    league = fields.UInt64Field(default=32)
    rank = fields.UInt64Field()

    engine = engines.MergeTree(partition_key=('toYYYYMMDD(day)',), order_by=('profile_id'))


class ProfileStatusDist(ProfileStatus, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class Registers(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    env = StringField()
    player_country = StringField()
    utm_campaign = StringField()
    utm_medium = StringField()
    utm_source = StringField()
    utm_full = StringField()
    platform_id = StringField()
    advertising_id = StringField() # MP only

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'platform_id'))


class RegistersDist(Registers, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class ResourcesLog(Model):
    day = DateField()
    profile_id = StringField()
    created_on = DateTimeField()
    actions = JsonStringField()
    difference = JsonStringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'profile_id'))


class ResourcesLogDist(ResourcesLog, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class Sessions(Model):
    day = DateField()
    event_type = StringField()
    created_on = DateTimeField()
    profile_id = StringField()
    session_id = StringField()
    env = StringField()
    device_id = StringField()
    player_country = StringField()
    platform_id = StringField()
    client_ip = StringField()
    login_id = StringField()
    request_id = StringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'event_type'))


class SessionsDist(Sessions, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class StartExperience(Model):
    day = DateField()
    created_on = DateTimeField()
    user_id = StringField()
    profile_id = StringField()
    event = StringField()
    utm_campaign = StringField()
    utm_content = StringField()
    description = StringField()
    seconds = StringField()
    new_user = StringField()
    referer = StringField()
    user_agent = StringField()

    engine = engines.ReplacingMergeTree(partition_key=('day',), order_by=('user_id',))


class StartExperienceDist(StartExperience, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)
