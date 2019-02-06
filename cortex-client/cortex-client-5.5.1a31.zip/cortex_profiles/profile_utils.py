import uuid

import pandas as pd

from cortex_profiles.types.insights import InsightTag, Link
from cortex_profiles import utils
from cortex_profiles.schemas.schemas import CONTEXTS
from cortex_profiles.profile_sessions_utils import associate_activity_with_sessions, derive_sessions_from_user_activity_df
from cortex_profiles.schemas.dataframes import INSIGHT_COLS, INTERACTIONS_COLS, SESSIONS_COLS, INSIGHT_ACTIVITY_COLS
import attr

def derive_sessions_from_user_activity(user_activity_df:pd.DataFrame, column_mapping:dict={}) -> pd.DataFrame:
    """
    :param user_activity_df: Needs a Data Frame that contains information regarding the following:
                1. The User With the Activity (profileId)
                2. The App the Activity was on (appId)
                3. The Start Time of the Activity as an 1SO UTC Date (isoUTCStartTime)
                4. The End Time of the Activity as an 1SO UTC Date (isoUTCEndTime)
    :param column_mapping: A dictionary mapping the names of the columns of the data frame that was passed in to the
                           columns expected as mentioned above ...
    :return: A dataframe of all the sessions derived ...
    """
    default_val = pd.DataFrame(columns = list(SESSIONS_COLS.keys()))
    return default_val if user_activity_df.empty else derive_sessions_from_user_activity_df(user_activity_df)


def associate_insight_activity_with_user_sessions(insight_activity_df:pd.DataFrame, sessions_df:pd.DataFrame, time_column:str) -> pd.DataFrame:
    """
    :param insights_df: A dataframe with insights that were presented that captures the following information:
                1. The User that was presented the insight (profileId)
                2. The App the Insight was presented on (appId)
                3. The Time the insight was presented as an 1SO UTC Date (isoUTCPresentedTime)
    :param sessions_df:
    :return:
    """
    return pd.concat(
        [
            ua_df.reset_index(drop=True).assign(
                sessionId=associate_activity_with_sessions(
                    ua_df.reset_index(drop=True).rename(columns={time_column:INSIGHT_ACTIVITY_COLS.ACTIVITY_TIME}),
                    sessions_df[(sessions_df[SESSIONS_COLS.PROFILEID] == user_app_pair[0]) & (sessions_df[SESSIONS_COLS.APPID] == user_app_pair[1])]
                )
            )
            for user_app_pair, ua_df in insight_activity_df.groupby([INSIGHT_ACTIVITY_COLS.PROFILEID, INSIGHT_ACTIVITY_COLS.APPID])
        ]
    )


def craft_tag_relating_insight_to_concept(insightId:str, conceptType:str, conceptId:str, conceptTitle:str, tagInsightAssociationDate:str) -> dict:
    if not utils.all_values_in_list_are_not_nones_or_nans([insightId, conceptType, conceptId, conceptTitle]):
        return {}
    return attr.asdict(InsightTag(
        id=utils.unique_id(),
        context=CONTEXTS.INSIGHT_CONCEPT_TAG,
        insight=Link(
            context=CONTEXTS.INSIGHT,
            id=insightId,
            title=None
        ),
        concept=Link(
            context=conceptType,
            id=conceptId,
            title=conceptTitle
        ),
        relationship=Link(
            context=CONTEXTS.INSIGHT_TAG_RELATIONSHIP,
            id=CONTEXTS.INSIGHT_TAG_RELATED_TO_RELATIONSHIP,
            title=None
        ),
        tagged=tagInsightAssociationDate # Knowing when this tag was associated with the insight is helpful for debuging ...!
    ))


def filter_insights_for_profile(insights_df:pd.DataFrame, profileId:str) -> pd.DataFrame:
    return insights_df[insights_df[INSIGHT_COLS.PROFILEID] == profileId]


def filter_interactions_for_profile(interactions_df:pd.DataFrame, profileId:str) -> pd.DataFrame:
    return interactions_df[interactions_df[INTERACTIONS_COLS.PROFILEID] == profileId]


def filter_sessions_for_profile(sessions_df:pd.DataFrame, profileId:str) -> pd.DataFrame:
    return sessions_df[sessions_df[SESSIONS_COLS.PROFILEID] == profileId]