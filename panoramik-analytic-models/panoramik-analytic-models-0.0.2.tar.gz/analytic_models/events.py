from infi.clickhouse_orm import fields, engines

from .fields import DateField, DateTimeField
from .db import CLUSTER_NAME, Model, DistributedModel


class EventQuestCompletion(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    league = fields.UInt64Field(default=32)
    event_id = fields.UInt64Field()
    quest_id = fields.UInt64Field()
    stars = fields.UInt64Field()
    chapter = fields.UInt64Field()

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class EventQuestCompletionDist(EventQuestCompletion, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class EventStart(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    league = fields.UInt64Field(default=32)
    event_id = fields.UInt64Field()

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class EventStartDist(EventStart, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class MiniEvents(Model):
    day = DateField()
    created_on = DateTimeField()
    profile_id = fields.StringField()
    action = fields.StringField()
    platform = fields.StringField()
    mini_event_id = fields.UInt64Field()

    engine = engines.MergeTree('day', ('profile_id', 'day'))


class MiniEventsDist(MiniEvents, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class QuestChapters(Model):
    day = DateField()
    event_id = fields.UInt64Field()
    chapter_number = fields.UInt32Field()
    chapter_id = fields.UInt32Field()

    engine = engines.MergeTree('day', ('chapter_id', 'day'))


class QuestChaptersDist(QuestChapters, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)


class QuestIds(Model):
    day = DateField()
    event_id = fields.UInt64Field()
    quest_id = fields.UInt64Field()
    chapter_id = fields.UInt32Field()

    engine = engines.MergeTree('day', ('quest_id', 'day'))

class QuestIdsDist(QuestIds, DistributedModel):
    engine = engines.Distributed(CLUSTER_NAME)
