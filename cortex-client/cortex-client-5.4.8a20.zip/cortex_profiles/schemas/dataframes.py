from cortex_profiles.utils import AttrsAsDict
import attr
from cortex_profiles.types.insights import Insight
from cortex_profiles.types.interactions import Session, InsightInteractionEvent


# - [ ] Function to auto derive df schema from name ...
# - [ ] Detail df schemas - Mark Unique Keys Mark Foreign Keys

class TAGGED_CONCEPT(AttrsAsDict):
    TYPE="taggedConceptType"
    RELATIONSHIP="taggedConceptRelationship"
    ID="taggedConceptId"
    TITLE="taggedConceptTitle"
    TAGGEDON="taggedOn"


class INTERACTION_DURATIONS_COLS(AttrsAsDict):
    STARTED_INTERACTION="startedInteractionISOUTC"
    STOPPED_INTERACTION="stoppedInteractionISOUTC"


class INSIGHT_COLS(AttrsAsDict):
    CONTEXT="context"
    ID="id"
    APPID=attr.fields(Insight).appId.name
    TAGS=attr.fields(Insight).tags.name
    INSIGHTTYPE=attr.fields(Insight).insightType.name
    PROFILEID=attr.fields(Insight).profileId.name
    DATEGENERATEDUTCISO=attr.fields(Insight).dateGeneratedUTCISO.name


class SESSIONS_COLS(AttrsAsDict):
    CONTEXT="context"
    ID="id"
    ISOUTCENDTIME=attr.fields(Session).isoUTCEndTime.name
    ISOUTCSTARTTIME=attr.fields(Session).isoUTCStartTime.name
    PROFILEID=attr.fields(Session).profileId.name
    APPID=attr.fields(Session).appId.name
    DURATIONINSECONDS=attr.fields(Session).durationInSeconds.name


class INTERACTIONS_COLS(AttrsAsDict):
    CONTEXT="context"
    ID="id"
    INTERACTIONTYPE=attr.fields(InsightInteractionEvent).interactionType.name
    INSIGHTID=attr.fields(InsightInteractionEvent).insightId.name
    PROFILEID=attr.fields(InsightInteractionEvent).profileId.name
    SESSIONID=attr.fields(InsightInteractionEvent).sessionId.name
    INTERACTIONDATEISOUTC=attr.fields(InsightInteractionEvent).interactionDateISOUTC.name
    PROPERTIES=attr.fields(InsightInteractionEvent).properties.name
    CUSTOM=attr.fields(InsightInteractionEvent).custom.name


class COUNT_OF_INTERACTIONS_COL(AttrsAsDict):
    PROFILEID=SESSIONS_COLS.PROFILEID
    INSIGHTTYPE=INSIGHT_COLS.INSIGHTTYPE
    INTERACTIONTYPE=INTERACTIONS_COLS.INTERACTIONTYPE
    TOTAL="total"


class COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL(AttrsAsDict):
    PROFILEID=SESSIONS_COLS.PROFILEID
    INSIGHTTYPE=INSIGHT_COLS.INSIGHTTYPE
    INTERACTIONTYPE=INTERACTIONS_COLS.INTERACTIONTYPE
    TAGGEDCONCEPTTYPE=TAGGED_CONCEPT.TYPE
    TAGGEDCONCEPTRELATIONSHIP=TAGGED_CONCEPT.RELATIONSHIP
    TAGGEDCONCEPTID=TAGGED_CONCEPT.ID
    TAGGEDCONCEPTTITLE=TAGGED_CONCEPT.TITLE
    TAGGEDON=TAGGED_CONCEPT.TAGGEDON
    TOTAL="total"


class TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL(AttrsAsDict):
    PROFILEID=SESSIONS_COLS.PROFILEID
    INSIGHTTYPE=INSIGHT_COLS.INSIGHTTYPE
    INTERACTIONTYPE=INTERACTIONS_COLS.INTERACTIONTYPE
    TAGGEDCONCEPTTYPE=TAGGED_CONCEPT.TYPE
    TAGGEDCONCEPTRELATIONSHIP=TAGGED_CONCEPT.RELATIONSHIP
    TAGGEDCONCEPTID=TAGGED_CONCEPT.ID
    TAGGEDCONCEPTTITLE=TAGGED_CONCEPT.TITLE
    TAGGEDON=TAGGED_CONCEPT.TAGGEDON
    ISOUTCSTARTTIME=INTERACTION_DURATIONS_COLS.STARTED_INTERACTION
    ISOUTCENDTIME=INTERACTION_DURATIONS_COLS.STOPPED_INTERACTION
    TOTAL="duration_in_seconds"


class INSIGHT_ACTIVITY_COLS(AttrsAsDict):
    ACTIVITY_TIME="isoUTCActivityTime"
    APPID=SESSIONS_COLS.APPID
    PROFILEID=SESSIONS_COLS.PROFILEID
    ISOUTCSTARTTIME=SESSIONS_COLS.ISOUTCSTARTTIME
    ISOUTCENDTIME=SESSIONS_COLS.ISOUTCENDTIME


class LOGIN_COUNTS_COL(AttrsAsDict):
    CONTEXT="context"
    ID="id"
    APPID=SESSIONS_COLS.APPID
    PROFILEID=SESSIONS_COLS.PROFILEID
    TOTAL="total_logins"


class LOGIN_DURATIONS_COL(AttrsAsDict):
    CONTEXT="context"
    ID="id"
    APPID=SESSIONS_COLS.APPID
    PROFILEID=SESSIONS_COLS.PROFILEID
    DURATION=SESSIONS_COLS.DURATIONINSECONDS


class DAILY_LOGIN_COUNTS_COL(AttrsAsDict):
    CONTEXT="context"
    ID="id"
    APPID=SESSIONS_COLS.APPID
    PROFILEID=SESSIONS_COLS.PROFILEID
    TOTAL="total_logins"
    DAY="day"


class DAILY_LOGIN_DURATIONS_COL(AttrsAsDict):
    CONTEXT="context"
    ID="id"
    APPID=SESSIONS_COLS.APPID
    PROFILEID=SESSIONS_COLS.PROFILEID
    DURATION=SESSIONS_COLS.DURATIONINSECONDS
    DAY="day"
