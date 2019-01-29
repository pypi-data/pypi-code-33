from infi.clickhouse_orm import fields, engines

from .fields import DateField, DateTimeField, BoolStringField, StringField
from .db import CLUSTER_NAME, Model, DistributedModel


class GuildshopItem(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    guild_id = fields.UInt64Field()
    item_id = fields.UInt64Field()
    item_level = fields.UInt64Field()
    league = fields.UInt64Field(default=32)

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'guild_id'))


class GuildshopItemDist(GuildshopItem, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class TroopsHiding(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    guild_id = fields.UInt64Field()
    guild_name = StringField()
    war_id = fields.UInt64Field()
    room_number = fields.UInt64Field()
    spent_gems = fields.UInt64Field()
    cell_x = fields.UInt64Field()
    cell_y = fields.UInt64Field()
    hidden = BoolStringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'war_id', 'room_number'))


class TroopsHidingDist(TroopsHiding, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)
