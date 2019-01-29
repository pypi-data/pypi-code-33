from infi.clickhouse_orm import fields, engines

from .fields import DateField, DateTimeField, BoolStringField, StringField
from .db import CLUSTER_NAME, Model, DistributedModel


class RaidBoosts(Model):
    day = DateField()
    created_on = DateTimeField()
    raid_id = fields.UInt64Field()
    room_number = fields.UInt64Field()
    room_group_number = fields.UInt64Field()
    start_datetime = DateTimeField()
    end_datetime = DateTimeField()
    is_qa_room = BoolStringField()
    profile_id = StringField()
    attack_boost = BoolStringField()
    spent_resource = fields.UInt64Field()
    times_boosted = fields.UInt64Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'raid_id', 'room_number'))


class RaidBoostsDist(RaidBoosts, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class RaidElixirSpent(Model):
    day = DateField()
    created_on = DateTimeField()
    raid_id = fields.UInt64Field()
    room_number = fields.UInt64Field()
    room_group_number = fields.UInt64Field()
    profile_id = StringField()
    action = StringField()
    elixir_spent = fields.UInt64Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'raid_id', 'room_number'))


class RaidElixirSpentDist(RaidElixirSpent, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class RaidForces(Model):
    day = DateField()
    created_on = DateTimeField()
    raid_id = fields.UInt64Field()
    room_number = fields.UInt64Field()
    room_group_number = fields.UInt64Field()
    start_datetime = DateTimeField()
    end_datetime = DateTimeField()
    is_qa_room = BoolStringField()
    profile_id = StringField()
    attack_force = BoolStringField()
    cell_x = fields.UInt64Field()
    cell_y = fields.UInt64Field()
    force_start_datetime = DateTimeField()
    power = fields.UInt64Field()
    pure_power = fields.UInt64Field()
    arrive_seconds = fields.UInt64Field()
    midway_seconds = fields.UInt64Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'raid_id', 'room_number'))


class RaidForcesDist(RaidForces, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class RaidRooms(Model):
    day = DateField()
    created_on = DateTimeField()
    raid_id = fields.UInt64Field()
    room_number = fields.UInt64Field()
    room_group_number = fields.UInt64Field()
    start_datetime = DateTimeField()
    end_datetime = DateTimeField()
    is_qa_room = BoolStringField()
    profile_id = StringField()
    start_raid_points = fields.UInt64Field()
    raid_points = fields.UInt64Field()
    static_raid_points = fields.UInt64Field()
    total_raid_points = fields.UInt64Field()
    start_total_raid_points = fields.UInt64Field()
    summary_guild_power = fields.UInt64Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'raid_id', 'room_number'))


class RaidRoomsDist(RaidRooms, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class RaidSpeedups(Model):
    day = DateField()
    created_on = DateTimeField()
    raid_id = fields.UInt64Field()
    room_number = fields.UInt64Field()
    room_group_number = fields.UInt64Field()
    start_datetime = DateTimeField()
    end_datetime = DateTimeField()
    is_qa_room = BoolStringField()
    profile_id = StringField()
    is_forward = BoolStringField()
    spent_resource = fields.UInt64Field()
    cell_x = fields.UInt64Field()
    cell_y = fields.UInt64Field()
    force_start_datetime = fields.UInt64Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'raid_id', 'room_number'))


class RaidSpeedupsDist(RaidSpeedups, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class RaidTroopsHiding(Model):
    day = DateField()
    created_on = DateTimeField()
    raid_id = fields.UInt64Field()
    room_number = fields.UInt64Field()
    room_group_number = fields.UInt64Field()
    start_datetime = DateTimeField()
    end_datetime = DateTimeField()
    is_qa_room = BoolStringField()
    profile_id = StringField()
    hidden = BoolStringField()
    spent_resource = fields.UInt64Field()
    cell_x = fields.UInt64Field()
    cell_y = fields.UInt64Field()
    force_start_datetime = DateTimeField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'raid_id', 'room_number'))


class RaidTroopsHidingDist(RaidTroopsHiding, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)

