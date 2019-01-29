from infi.clickhouse_orm import fields, engines

from .fields import DateField, DateTimeField, BoolStringField
from .db import CLUSTER_NAME, Model, DistributedModel


class DungeonBattle(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    level_id = fields.StringField()
    is_win = BoolStringField()
    monster_id = fields.StringField()
    monster_souls = fields.StringField()
    monster_rarity = fields.StringField()
    league = fields.UInt64Field(default=32)

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class DungeonBattleDist(DungeonBattle, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class Pits(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    action = fields.StringField()
    league = fields.UInt64Field(default=32)
    pit_id = fields.UInt64Field()
    pit_level = fields.StringField()
    start_datetime = fields.StringField()
    current_hp = fields.StringField()
    bought_pit_keys = fields.UInt64Field()
    spent_gems = fields.UInt64Field()

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class PitsDist(Pits, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class PvpStats(Model):
    day = DateField()
    created_on = DateTimeField()
    finished_on = DateTimeField()
    attacker_id = fields.StringField()
    defender_id = fields.StringField()
    match_type = fields.StringField()
    match_id = fields.UInt64Field()
    fame = fields.UInt64Field()
    league = fields.UInt64Field(default=32)
    strike = fields.UInt64Field()
    is_win = BoolStringField()
    attacker_win_fame_change = fields.StringField()
    attacker_lose_fame_change = fields.StringField()
    attacker_start_fame = fields.StringField()
    attacker_start_base_collection_armypower = fields.StringField()
    attacker_start_collection_armypower = fields.StringField()
    is_first = fields.StringField()
    survival_strike = fields.StringField()
    enemy_warlord_hp = fields.StringField()
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

    engine = engines.MergeTree('day', ('attacker_id', 'day'))


class PvpStatsDist(PvpStats, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class PvpWarlordSkin(Model):
    day = DateField()
    created_on = DateTimeField()
    attacker_id = fields.StringField()
    opponent_id = fields.StringField()
    league = fields.StringField(default='32')
    match_id = fields.StringField()
    skin_id = fields.StringField()

    engine = engines.MergeTree('day', ('attacker_id', 'day'))


class PvpWarlordSkinDist(PvpWarlordSkin, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class TavernBattle(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    level_id = fields.StringField()
    is_win = BoolStringField()
    tavern_id = fields.StringField()
    warlord_id = fields.StringField()
    league = fields.UInt64Field(default=32)

    engine = engines.MergeTree('day', ('day', 'profile_id'))


class TavernBattleDist(TavernBattle, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)
