from infi.clickhouse_orm import fields, engines

from .fields import DateField, DateTimeField, ListStringField, BoolStringField, StringField
from .db import CLUSTER_NAME, Model, DistributedModel


class EventLot(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    league = fields.UInt64Field(default=32)
    event_id = fields.UInt64Field()
    lot_string_id = StringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'profile_id'))


class EventLotDist(EventLot, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class EventShopLot(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    league = fields.UInt64Field(default=32)
    event_id = fields.UInt64Field()
    lot_id = fields.UInt64Field()
    price = fields.Float64Field()
    platform_id = StringField() # queue only
    env = StringField() # queue only

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'event_id'))


class EventShopLotDist(EventShopLot, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class EventTotalPurchases(Model):
    event_id = fields.UInt64Field() # in AP only
    quest_id = fields.UInt64Field()
    price = fields.Float64Field()

    engine = engines.Log()


class ItemShown(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    session_id = StringField()
    item_types = ListStringField()
    item_ids = ListStringField()
    item_info = StringField()
    source = StringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on',))


class ItemShownDist(ItemShown, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class LotApplied(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    item_id = StringField()
    price = fields.Float64Field()
    price_res_type = StringField()
    action_id = StringField()
    environment = StringField() # TODO add to table

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'item_id'))


class LotAppliedDist(LotApplied, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class Purchases(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    league = fields.UInt64Field(default=32)
    lot_id = StringField()
    lot_string_id = StringField()
    environment = StringField()
    transaction_id = StringField()
    is_qa_purchase = BoolStringField()
    currency_code = StringField()
    state = StringField()
    price = fields.Float64Field()
    price_usd = fields.Float64Field()
    rank = fields.UInt64Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'environment'))


class PurchasesDist(Purchases, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


# class QuestLotId(Model):
#     event_id = fields.UInt64Field()
#     lot_id = fields.UInt64Field()
#     shop_lot = fields.UInt32Field()
#
#     engine = engines.Log()


# class QuestShopLots(Model):
#     quest_id = fields.UInt64Field()
#     chapter_id = fields.UInt64Field()
#     shop_lot = fields.UInt32Field()
#
#     engine = engines.Log()


class SkinPurchase(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    platform = StringField()
    league = fields.UInt64Field(default=32)
    skin_id = StringField()
    price = StringField()
    price_resource = StringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'skin_id'))


class SkinPurchaseDist(SkinPurchase, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)
