from infi.clickhouse_orm import fields, engines

from .fields import DateField, DateTimeField, ListStringField, BoolStringField
from .db import CLUSTER_NAME, Model, DistributedModel


class EventLot(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    league = fields.UInt64Field(default=32)
    event_id = fields.UInt64Field()
    lot_string_id = fields.StringField()

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class EventLotDist(EventLot, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class EventShopLot(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    league = fields.UInt64Field(default=32)
    event_id = fields.UInt64Field()
    lot_id = fields.UInt64Field()
    price = fields.Float64Field()
    platform_id = fields.StringField() # queue only
    env = fields.StringField() # queue only

    engine = engines.MergeTree('day', ('profile_id', 'day'))


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
    profile_id = fields.StringField()
    item_types = ListStringField()
    item_ids = ListStringField()

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class ItemShownDist(ItemShown, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class LotApplied(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    item_id = fields.StringField()
    price = fields.Float64Field()
    price_res_type = fields.StringField()
    action_id = fields.StringField()

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class LotAppliedDist(LotApplied, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class Purchases(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    league = fields.UInt64Field(default=32)
    lot_id = fields.StringField()
    lot_string_id = fields.StringField()
    environment = fields.StringField()
    transaction_id = fields.StringField()
    is_qa_purchase = BoolStringField()
    currency_code = fields.StringField()
    state = fields.StringField()
    price = fields.Float64Field()
    price_usd = fields.Float64Field()
    rank = fields.UInt64Field()

    engine = engines.MergeTree('day', ('profile_id', 'day'))


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
    profile_id = fields.StringField()
    platform = fields.StringField()
    league = fields.UInt64Field(default=32)
    skin_id = fields.StringField()
    price = fields.StringField()
    price_resource = fields.StringField()

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class SkinPurchaseDist(SkinPurchase, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)
