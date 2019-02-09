from typing import List

import attr
from cortex_profiles.utils import list_converter, attr_fields_except
from cortex_profiles.schemas.schemas import TIMEFRAMES


@attr.s(frozen=True)
class OptionalDescriber(object):
    id = attr.ib(type=str)
    adjective = attr.ib(type=str)
    adverb = attr.ib(type=str)
    include = attr.ib(type=bool)
    optionalAdjective = attr.ib(type=str)
    optionalAdverb = attr.ib(type=str)

    @optionalAdjective.default
    def defaultOptionalAdjective(self):
        if self.include:
            return self.adjective
        return ""

    @optionalAdverb.default
    def defaultOptionalAdverb(self):
        if self.include:
            return self.adverb
        return ""


@attr.s(frozen=True, auto_attribs=True)
class Subject(object):
    id: str
    singular: str = ""
    plural: str = ""
    acronym: str = ""


@attr.s(frozen=True)
class Verb(object):
    id = attr.ib(type=str)
    verb = attr.ib(type=str)
    verbInitiatedBySubject = attr.ib(type=bool)
    verbStatement = attr.ib(type=str)

    @verbStatement.default
    def defaultVerbStatement(self):
        return "{} to".format(self.verb) if not self.verbInitiatedBySubject else "{} by".format(self.verb)

implicit_timeframes = list_converter(
    [
        {"id": TIMEFRAMES.RECENT,  "adjective": "recent",   "adverb": "recently",  "include": True},
        {"id": TIMEFRAMES.HISTORIC, "adjective": "eternal",  "adverb": "eternally", "include": False}
    ],
    OptionalDescriber
)

@attr.s(frozen=True)
class SchemaConfig(object):
    apps = attr.ib(type=List[Subject], converter=lambda l: list_converter(l, Subject))
    insight_types = attr.ib(type=List[Subject], converter=lambda l: list_converter(l, Subject))
    concepts = attr.ib(type=List[Subject], converter=lambda l: list_converter(l, Subject))
    interaction_types = attr.ib(type=List[Verb], converter=lambda l: list_converter(l, Verb))
    timed_interaction_types = attr.ib(type=List[Verb], converter=lambda l: list_converter(l, Verb))
    timeframes = attr.ib(type=List[OptionalDescriber], factory=lambda:implicit_timeframes, converter=lambda l: list_converter(l, OptionalDescriber))


CONCEPT_SPECIFIC_INTERACTION_FIELDS = attr_fields_except(SchemaConfig, [attr.fields(SchemaConfig).timed_interaction_types, attr.fields(SchemaConfig).apps])
CONCEPT_SPECIFIC_DURATION_FIELDS = attr_fields_except(SchemaConfig, [attr.fields(SchemaConfig).interaction_types, attr.fields(SchemaConfig).apps])
INTERACTION_FIELDS = [attr.fields(SchemaConfig).timeframes, attr.fields(SchemaConfig).insight_types, attr.fields(SchemaConfig).interaction_types]
APP_SPECIFIC_FIELDS = [attr.fields(SchemaConfig).timeframes, attr.fields(SchemaConfig).apps]
