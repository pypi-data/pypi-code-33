from typing import Optional, List

from cortex_profiles.utils import unique_id, utc_timestamp
from attr import attrs, Factory
from cortex_profiles.schemas.schemas import VERSION, CONTEXTS


@attrs(frozen=True, auto_attribs=True)
class Link(object):
    id: str  # What is the id of this piece of data?
    context: str  # What is the type of the data being captured by this data type?
    version: str = VERSION  # What version of the data type is being adhered to?
    title: Optional[str] = None # What is the human friendly name of this link?


@attrs(frozen=True, auto_attribs=True)
class InsightTag(object):
    id: str  # What is the id of this piece of data?
    insight: Link  # What insight is this tag about?
    tagged: str  # When was the insight tagged with this tag?
    concept: Link  # What concept is being tagged by the insight?
    relationship: Link  # What relationship does the tagged concept have with regards to the insight?
    context: str = CONTEXTS.INSIGHT_CONCEPT_TAG  # What is the type of the data being captured by this data type?
    version: str = VERSION  # What version of the data type is being adhered to?


@attrs(frozen=True, auto_attribs=True)
class Insight(object):
    id: str  # What is the id of this piece of data?
    insightType: str # What kind of insight is this?
    profileId: str # What profile was this insight generated for?
    dateGeneratedUTCISO: str # When was this insight generated?
    appId: str # Which app was this insight generated for?
    tags: List[InsightTag] = Factory(list) # What concepts were tagged in this insight?
    context: str = CONTEXTS.INSIGHT  # What is the type of the data being captured by this data type?
    version: str = VERSION  # What version of the data type is being adhered to?


@attrs(frozen=True, auto_attribs=True)
class InsightRelatedToConceptTag(InsightTag):
    """
    Representing how an insight relates to other concepts ...
    """
    id: str = Factory(unique_id)
    tagged: str = Factory(utc_timestamp)
    relationship: Link = Link(id=CONTEXTS.INSIGHT_TAG_RELATED_TO_RELATIONSHIP, context=CONTEXTS.INSIGHT_TAG_RELATIONSHIP)


