from typing import Optional

from attr import attrs
from cortex_profiles.schemas.schemas import CONTEXTS, VERSION


@attrs(frozen=True, auto_attribs=True)
class UserActivity(object):
    context: str  # What is the type of the data being captured by this data type?
    id: str  # What is the id of this piece of data?
    profileId: str # What profile initiated the activity?
    appId: str # Which app did this activity occur on?
    isoUTCStartTime: str # When did this activity start?
    isoUTCEndTime: str # When did this activity end?


@attrs(frozen=True, auto_attribs=True)
class Session(object):
    id: str  # What is the id of this piece of data?
    profileId: str  # What profile initiated the activity?
    appId: str  # Which app did this activity occur on?
    isoUTCStartTime: str  # When did this activity start?
    isoUTCEndTime: str  # When did this activity end?
    durationInSeconds: float # How long did the session last?
    context: str = CONTEXTS.SESSION  # What is the type of the data being captured by this data type?
    version: str = VERSION  # What version of the data type is being adhered to?


@attrs(frozen=True, auto_attribs=True)
class InsightInteractionEvent(object):
    id: str  # What is the id of this piece of data?
    sessionId:str # What session did the interaction occur in?
    profileId: str  # Which profile was responsible for this interaction?
    insightId:str # Which insight's was interacted on?
    interactionType:str # What type of interaction was performed on the insight? TODO ... what is the list of interaction types?
    interactionDateISOUTC:str # When did the insight transition to this state?
    properties: dict # What additional information is needed when transitioning into a specific state?
    custom:Optional[dict] # Is there any use case specific stuff we need to know about the interaction?
    version: str = VERSION  # What version of the data type is being adhered to?
    context: str = CONTEXTS.INSIGHT_INTERACTION  # What is the type of the data being captured by this data type?
