from infi.clickhouse_orm import fields, engines

from .fields import DateField, DateTimeField, BoolStringField, StringField
from .db import CLUSTER_NAME, Model, DistributedModel


class DungeonBattle(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    level_id = StringField()
    is_win = BoolStringField()
    monster_id = StringField()
    monster_souls = StringField()
    monster_rarity = StringField()
    league = fields.UInt64Field(default=32)

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'profile_id'))


class DungeonBattleDist(DungeonBattle, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class Pits(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    action = StringField()
    league = fields.UInt64Field(default=32)
    pit_id = fields.UInt64Field()
    pit_level = StringField()
    start_datetime = StringField()
    current_hp = StringField()
    bought_pit_keys = fields.UInt64Field()
    spent_gems = fields.UInt64Field()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'pit_id'))


class PitsDist(Pits, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class PvpStats(Model):
    day = DateField()
    created_on = DateTimeField()
    finished_on = DateTimeField()
    attacker_id = StringField()
    defender_id = StringField()
    match_type = StringField()
    match_id = fields.UInt64Field()
    fame = fields.UInt64Field()
    league = fields.UInt64Field(default=32)
    strike = fields.UInt64Field()
    is_win = BoolStringField()
    attacker_win_fame_change = StringField()
    attacker_lose_fame_change = StringField()
    attacker_start_fame = StringField()
    attacker_start_base_collection_armypower = StringField()
    attacker_start_collection_armypower = StringField()
    is_first = StringField()
    survival_strike = StringField()
    enemy_warlord_hp = StringField()
    attacker_survival_base_collection_armypower = fields.Float64Field()
    attacker_survival_collection_armypower = fields.Float64Field() # MP Default 0.
    defender_survival_base_collection_armypower = fields.Float64Field() # MP Default 0.
    defender_survival_collection_armypower = fields.Float64Field() # MP Default 0.
    attacker_base_armypower = fields.Float64Field()
    attacker_cur_armypower = fields.Float64Field()
    attacker_max_armypower = fields.Float64Field()
    defender_base_armypower = fields.Float64Field()
    defender_cur_armypower = fields.Float64Field()
    defender_max_armypower = fields.Float64Field()
    battle_time = fields.UInt64Field()  # TODO add to table

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'match_type'))


class PvpStatsDist(PvpStats, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class PvpWarlordSkin(Model):
    day = DateField()
    created_on = DateTimeField()
    attacker_id = StringField()
    opponent_id = StringField()
    league = StringField(default='32')
    match_id = StringField()
    skin_id = StringField()

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'skin_id'))


class PvpWarlordSkinDist(PvpWarlordSkin, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class TavernBattle(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = StringField()
    level_id = StringField()
    is_win = BoolStringField()
    tavern_id = StringField()
    warlord_id = StringField()
    league = fields.UInt64Field(default=32)

    engine = engines.MergeTree(partition_key=('day',), order_by=('created_on', 'tavern_id'))


class TavernBattleDist(TavernBattle, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)
