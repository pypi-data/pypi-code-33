from cortex_profiles.schemas.dataframes import TAGGED_CONCEPT, INSIGHT_COLS, SESSIONS_COLS, INTERACTIONS_COLS

INSIGHT_TYPE = INSIGHT_COLS.INSIGHTTYPE
INTERACTION_TYPE = INTERACTIONS_COLS.INTERACTIONTYPE
CONCEPT = TAGGED_CONCEPT.TYPE
APP_ID = SESSIONS_COLS.APPID
TIMEFRAME = "TIMEFRAME"


attr_name_config_pattern = {
    "insight_type": INSIGHT_TYPE,
    "interaction_type": INTERACTION_TYPE,
    "concept_title": CONCEPT,
    "app_id": APP_ID,
    "timeframe": TIMEFRAME,
}

attr_schema_config_patterns = {
    "insight_type": "{}.plural".format(INSIGHT_TYPE),
    "interaction_type": "{}.verbStatement".format(INTERACTION_TYPE),
    "plural_concept_title": "{}.plural".format(CONCEPT),
    "singular_concept_title": "{}.singular".format(CONCEPT),
    "app_title": "{}.acronym".format(APP_ID),
    "optional_timeframe_adverb": "{}.optionalAdverb".format(TIMEFRAME),
    "optional_timeframe_adjective": "{}.optionalAdjective".format(TIMEFRAME),
}

tag_schema_config_patterns = {
    "app_id": "{}.id".format(APP_ID),
    "app_name": "{}.singular".format(APP_ID),
    "app_symbol": "{}.acronym".format(APP_ID),

    "insight_type_id": "{}.id".format(INSIGHT_TYPE),
    "insight_type": "{}.singular".format(INSIGHT_TYPE),
    "insight_type_symbol": "{}.acronym".format(INSIGHT_TYPE),

    "concept_id": "{}.id".format(CONCEPT),
    "concepts": "{}.plural".format(CONCEPT),

    "interaction_type": "{}.id".format(INTERACTION_TYPE),
    "interaction_statement": "{}.verbStatement".format(INTERACTION_TYPE),
}


def attr_name_template(s:str) -> str:
    return s.format(**attr_name_config_pattern)


def attr_template(s:str) -> str:
    return s.format(**attr_schema_config_patterns)


def tag_template(s:str) -> str:
    return s.format(**tag_schema_config_patterns)