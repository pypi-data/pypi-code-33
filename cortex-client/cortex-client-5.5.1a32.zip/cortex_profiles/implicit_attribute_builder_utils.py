from collections import Counter
from typing import List, Tuple

import pandas as pd
from cortex_profiles import implicit_attribute_builder_utils, utils_for_dfs
from cortex_profiles.schemas.dataframes import COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL, SESSIONS_COLS, \
    TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL, INSIGHT_COLS, INTERACTIONS_COLS, DAILY_LOGIN_COUNTS_COL, \
    LOGIN_COUNTS_COL, LOGIN_DURATIONS_COL, INTERACTION_DURATIONS_COLS, DAILY_LOGIN_DURATIONS_COL
from cortex_profiles.schemas.schemas import CONTEXTS, INTERACTIONS
from cortex_profiles.utils import derive_day_from_date, derive_hour_from_date


def merge_interactions_with_insights(insight_interactions_df:pd.DataFrame, insights_df:pd.DataFrame) -> pd.DataFrame:
    """
    This method not only does a LEFT JOIN of the interaction table with the insight table ...
    it also expands the joined result such that there is a record for each tag an insight was tagged with ...
    Essentially ... its creating a table of interactions per insight tag ...

    :param insight_interactions_df:
    :param insights_df:
    :return:
    """
    subset_of_insights = insights_df[[INSIGHT_COLS.ID, INSIGHT_COLS.INSIGHTTYPE, INSIGHT_COLS.TAGS]].rename(columns={INSIGHT_COLS.ID: INTERACTIONS_COLS.INSIGHTID})
    merged_interactions_with_insights = pd.merge(
            insight_interactions_df, subset_of_insights, on=INTERACTIONS_COLS.INSIGHTID, how="left"
        ).drop(
            [INTERACTIONS_COLS.PROPERTIES, INTERACTIONS_COLS.CUSTOM], # These cant be in the dict when a column is exploded since they are not hashable ...
            axis=1
        )
    return implicit_attribute_builder_utils.expand_tag_column(
        utils_for_dfs.explode_column(merged_interactions_with_insights, INSIGHT_COLS.TAGS), INSIGHT_COLS.TAGS
    )


# --------------------------------------------------------------------------------------------------------------------


def derive_count_of_insights_per_interactionType_per_insightType_per_profile(insight_interactions_df: pd.DataFrame, insights_df: pd.DataFrame) -> pd.DataFrame :
    """
    For every profile, what is the total count of insights relevant to the profile that the profile interacted with in
        different ways {liked, disliked, ...} per type of insight {Investmnet Insight, Retirement, ...}
    :param insight_interactions_df:
    :param insights_df:
    :return:
    """
    insight_transitions_events_with_types = pd.merge(
        insight_interactions_df,
        insights_df[[INSIGHT_COLS.ID, INSIGHT_COLS.INSIGHTTYPE]],
        left_on=INTERACTIONS_COLS.INSIGHTID, right_on=INSIGHT_COLS.ID, how="inner"
    )
    return implicit_attribute_builder_utils.determine_count_of_occurrences_of_grouping(
        insight_transitions_events_with_types, [INTERACTIONS_COLS.PROFILEID, INSIGHT_COLS.INSIGHTTYPE, INTERACTIONS_COLS.INTERACTIONTYPE]
    )


# def derive_count_of_recent_insights_per_interactionType_per_insightType_per_profile(insight_interactions_df: pd.DataFrame, insights_df: pd.DataFrame) -> pd.DataFrame :
#     """
#     For every profile, what is the total number count of insights relevant to the profile that the profile RECENTLY
#         interacted with in different ways {liked, disliked, ...} per type of insight {Investment Insight, Retirement, ...}
#     :param insight_interactions_df:
#     :param insights_df:
#     :return:
#     """
#     return derive_count_of_insights_per_interactionType_per_insightType_per_profile(
#         utils_for_dfs.filter_time_column_after(insight_interactions_df, INTERACTIONS_COLS.INTERACTIONDATEISOUTC, {"days": -14}),
#         insights_df
#     )


# --------------------------------------------------------------------------------------------------------------------


def derive_count_of_insights_per_interactionType_per_relatedConcepts_per_profile(
        insight_interactions_df: pd.DataFrame, insights_df: pd.DataFrame) -> pd.DataFrame :
    """
    For every profile, what is the total number count of insights relevant to the profile that transitioned
        to each of the different states {liked, disliked, ...} per related concept {Investment Insight, Retirement, ...}
    :param insight_interactions_df:
    :param insights_df:
    :return:
    """

    expanded_insight_interactions_df = merge_interactions_with_insights(insight_interactions_df, insights_df)

    filtered_interactions_with_tags = expanded_insight_interactions_df[
        expanded_insight_interactions_df[COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTRELATIONSHIP] == CONTEXTS.INSIGHT_TAG_RELATED_TO_RELATIONSHIP
        ]

    return filtered_interactions_with_tags.assign(total=1).groupby(
        [
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.PROFILEID,
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.INSIGHTTYPE,
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.INTERACTIONTYPE,
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTTYPE,
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTRELATIONSHIP,
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTID,
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTTITLE,  # Not really an id ... but wanted to preserve it post agg ...
        ]
    ).agg({
        COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TOTAL: 'size',
        COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDON: lambda x: list(sorted(x))
    }).reset_index()


def derive_count_of_insights_per_interactionType_per_relatedConcepts(
        insight_interactions_df: pd.DataFrame, insights_df: pd.DataFrame) -> pd.DataFrame :
    """
    What is the total number of insights that transitioned to each of the different states {liked, disliked, ...}
        per related concept {Investment Insight, Retirement, ...}
    :param insight_interactions_df:
    :param insights_df:
    :return:
    """

    expanded_insight_interactions_df = merge_interactions_with_insights(insight_interactions_df, insights_df)

    filtered_interactions_with_tags = expanded_insight_interactions_df[
        expanded_insight_interactions_df[COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTRELATIONSHIP] == CONTEXTS.INSIGHT_TAG_RELATED_TO_RELATIONSHIP
        ]

    return filtered_interactions_with_tags.assign(total=1).groupby(
        [
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.INSIGHTTYPE,
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.INTERACTIONTYPE,
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTTYPE,
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTRELATIONSHIP,
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTID,
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTTITLE,
        ]
    ).agg({
        COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TOTAL: 'size',
        COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDON: lambda x: list(sorted(x))
    }).reset_index()


# def derive_count_of_recent_insights_per_interactionType_per_relatedConcepts_per_profile(
#         insight_interactions_df: pd.DataFrame, insights_df: pd.DataFrame) -> pd.DataFrame :
#     """
#     For every profile, what is the total number count of insights relevant to the profile that transitioned
#         to each of the different states {liked, disliked, ...} per related concept {Investment Insight, Retirement, ...}
#     :param insight_interactions_df:
#     :param insights_df:
#     :return:
#     """
#     return derive_count_of_insights_per_interactionType_per_relatedConcepts_per_profile(
#         utils_for_dfs.filter_time_column_after(insight_interactions_df, INTERACTIONS_COLS.INTERACTIONDATEISOUTC, {"days": -14}),
#         insights_df
#     )


# --------------------------------------------------------------------------------------------------------------------


def prepare_interactions_per_tag_with_times(insight_interactions_df:pd.DataFrame, insights_df:pd.DataFrame) -> pd.DataFrame :

    expanded_insight_interactions_df = merge_interactions_with_insights(
        implicit_attribute_builder_utils.append_interaction_time_to_df_from_properties(insight_interactions_df),
        insights_df
    )
    if expanded_insight_interactions_df.empty:
        return pd.DataFrame(columns=TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.values())
    interactions_about_related_concepts_mask = expanded_insight_interactions_df[TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTRELATIONSHIP] == CONTEXTS.INSIGHT_TAG_RELATED_TO_RELATIONSHIP
    interactions_about_views_mask = expanded_insight_interactions_df[TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.INTERACTIONTYPE] == INTERACTIONS.VIEWED
    filtered_interactions_with_times = expanded_insight_interactions_df[(interactions_about_related_concepts_mask) & (interactions_about_views_mask)]
    return filtered_interactions_with_times



def derive_time_spent_on_insights_with_relatedConcepts(insight_interactions_with_time_df: pd.DataFrame) -> pd.DataFrame :
    return utils_for_dfs.append_seconds_to_df(
            insight_interactions_with_time_df,
            TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TOTAL,
            TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.ISOUTCSTARTTIME,
            TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.ISOUTCENDTIME
        ).groupby([
            TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.PROFILEID,
            TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.INSIGHTTYPE,
            TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.INTERACTIONTYPE,
            TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTTYPE,
            TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTID,
            TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTRELATIONSHIP,
            TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTTITLE,  # Not really an id ... but wanted to preserve it post agg ...
        ]).agg({
            TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TOTAL: 'sum',
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDON: lambda x: list(sorted(x))
        }).reset_index()


# ----------------------------------------------------------------------


def derive_count_of_user_logins(sessions_df:pd.DataFrame) -> pd.DataFrame:
    return implicit_attribute_builder_utils.determine_count_of_occurrences_of_grouping(
        sessions_df[[
            LOGIN_COUNTS_COL.PROFILEID,
            LOGIN_COUNTS_COL.APPID,
            # LOGIN_COUNTS_COL.ISOUTCSTARTTIME,
        ]],
        [
            LOGIN_COUNTS_COL.PROFILEID,
            LOGIN_COUNTS_COL.APPID
        ],
        LOGIN_COUNTS_COL.TOTAL
    )


# def derive_count_of_recent_user_logins(sessions_df:pd.DataFrame) -> pd.DataFrame:
#     return derive_count_of_user_logins(implicit_attribute_builder_utils.filter_recent_sessions(sessions_df))


# ----------------------------------------------------------------------


def derive_time_users_spent_logged_in(sessions_df:pd.DataFrame) -> pd.DataFrame:
    return implicit_attribute_builder_utils.determine_time_spent_on_occurrences_of_grouping(
        sessions_df,
        [LOGIN_DURATIONS_COL.PROFILEID, LOGIN_DURATIONS_COL.APPID],
        LOGIN_DURATIONS_COL.DURATION
    )


# def derive_time_user_recently_spent_logged_in(sessions_df:pd.DataFrame) -> pd.DataFrame:
#     return derive_time_users_spent_logged_in(implicit_attribute_builder_utils.filter_recent_sessions(sessions_df))


# ----------------------------------------------------------------------


def derive_daily_login_counts(sessions_df:pd.DataFrame) -> pd.DataFrame:
    """
    #Refactor: Can I use the profile instead of the logins df?
    #Refactor: Can I adjust day based on timezone if available ...
        # - If you learned someone's timezone ... do you have to shift all of the historic data? or only the new stuff you are computing???
    :param logins_df:
    :return:
    """
    daily_logins = [
        implicit_attribute_builder_utils.derive_total_logins_on_specific_dates(user_app_tuple, sessions_df)
        for user_app_tuple, sessions_df in sessions_df.groupby([DAILY_LOGIN_COUNTS_COL.PROFILEID, DAILY_LOGIN_COUNTS_COL.APPID])
    ]
    return pd.concat(daily_logins, ignore_index=True) if daily_logins else pd.DataFrame(columns=list(sessions_df.columns) + [DAILY_LOGIN_COUNTS_COL.DAY])



# def derive_recent_daily_login_counts(sessions_df:pd.DataFrame) -> pd.DataFrame:
#     return derive_daily_login_counts(implicit_attribute_builder_utils.filter_recent_sessions(sessions_df))


def derive_average_of_daily_login_counts(sessions_df:pd.DataFrame) -> pd.DataFrame:
    daily_login_count_df = derive_daily_login_counts(sessions_df)
    columns_to_keep = [DAILY_LOGIN_COUNTS_COL.PROFILEID, DAILY_LOGIN_COUNTS_COL.APPID, DAILY_LOGIN_COUNTS_COL.DAY, DAILY_LOGIN_COUNTS_COL.TOTAL]
    return daily_login_count_df[columns_to_keep].groupby([
        DAILY_LOGIN_COUNTS_COL.APPID, DAILY_LOGIN_COUNTS_COL.PROFILEID
    ]).mean().reset_index() if (not daily_login_count_df.empty) else pd.DataFrame(columns=columns_to_keep)


# def derive_recent_average_of_daily_login_counts(sessions_df:pd.DataFrame) -> pd.DataFrame:
#     return derive_average_of_daily_login_counts(implicit_attribute_builder_utils.filter_recent_sessions(sessions_df))


# ----------------------------------------------------------------------


def derive_daily_login_duration(logins_df:pd.DataFrame) -> pd.DataFrame:
    login_dfs = [
        implicit_attribute_builder_utils.derive_user_date_login_duration_df(user_app_tuple, user_logins_df)
        for user_app_tuple, user_logins_df in logins_df.groupby([DAILY_LOGIN_DURATIONS_COL.PROFILEID, DAILY_LOGIN_DURATIONS_COL.APPID])
    ]
    return pd.concat(login_dfs, ignore_index=True) if login_dfs else pd.DataFrame(columns=list(logins_df.columns) + [DAILY_LOGIN_DURATIONS_COL.DAY])

def derive_recent_daily_login_duration(sessions_df:pd.DataFrame) -> pd.DataFrame:
    return derive_daily_login_duration(implicit_attribute_builder_utils.filter_recent_sessions(sessions_df))


def derive_average_of_daily_login_durations(sessions_df:pd.DataFrame) -> pd.DataFrame:
    columns_to_keep = [SESSIONS_COLS.PROFILEID, SESSIONS_COLS.APPID, SESSIONS_COLS.DURATIONINSECONDS]
    return derive_daily_login_duration(sessions_df)[columns_to_keep].groupby(
        [SESSIONS_COLS.PROFILEID, SESSIONS_COLS.APPID]
    ).mean().reset_index() if not sessions_df.empty else pd.DataFrame(columns=columns_to_keep)


def derive_average_of_recent_daily_login_durations(sessions_df:pd.DataFrame) -> pd.DataFrame:
    return derive_average_of_daily_login_durations(implicit_attribute_builder_utils.filter_recent_sessions(sessions_df))


# --------------------------------------------------------------------------------------------


def append_interaction_time_to_df_from_properties(df:pd.DataFrame) -> pd.DataFrame:
    return df.assign(**{
        INTERACTION_DURATIONS_COLS.STARTED_INTERACTION: df["properties"].map(
            lambda x: x.get(INTERACTION_DURATIONS_COLS.STARTED_INTERACTION)),
        INTERACTION_DURATIONS_COLS.STOPPED_INTERACTION: df["properties"].map(
            lambda x: x.get(INTERACTION_DURATIONS_COLS.STOPPED_INTERACTION)),
    })


def determine_count_of_occurrences_of_grouping(df:pd.DataFrame, grouping:List[str], count_column_name:str="total") -> pd.DataFrame :
    return (
        df.groupby(grouping).size().reset_index().rename(columns={0: count_column_name}) if not df.empty else
        pd.DataFrame(columns=grouping + [count_column_name])
    )



def determine_time_spent_on_occurrences_of_grouping(df:pd.DataFrame, grouping:List[str], time_duration_col:str) -> pd.DataFrame :
    return df[grouping+[time_duration_col]].groupby(grouping).sum().reset_index()


def derive_user_date_login_duration_df(user_app_tuple:str, sessions_df:pd.DataFrame) -> pd.DataFrame:
    user_login_duration_df = sessions_df.reset_index()
    user_login_duration_df[DAILY_LOGIN_DURATIONS_COL.DAY] = user_login_duration_df[SESSIONS_COLS.ISOUTCSTARTTIME].map(derive_day_from_date)
    user_login_duration_df = determine_time_spent_on_occurrences_of_grouping(
        user_login_duration_df,
        [DAILY_LOGIN_DURATIONS_COL.APPID, DAILY_LOGIN_DURATIONS_COL.PROFILEID, DAILY_LOGIN_DURATIONS_COL.DAY],
        DAILY_LOGIN_DURATIONS_COL.DURATION
    )
    return user_login_duration_df


# def derive_recent_logins(logins_df:pd.DataFrame) -> pd.DataFrame :
#     return helpers_for_dfs.filter_time_column_within(logins_df, "loggedIn", {"days":-14})


def filter_recent_insights(insights_df:pd.DataFrame, days_considered_recent=14) -> pd.DataFrame:
    return filter_recent_records_on_column(insights_df, INSIGHT_COLS.DATEGENERATEDUTCISO, days_considered_recent)


def filter_insights_before(insights_df:pd.DataFrame, days:int) -> pd.DataFrame:
    return utils_for_dfs.filter_time_column_before(insights_df, INSIGHT_COLS.DATEGENERATEDUTCISO, {"days":-1*days})


def filter_recent_interactions(interactions_df:pd.DataFrame, days_considered_recent=14) -> pd.DataFrame:
    return filter_recent_records_on_column(interactions_df, INTERACTIONS_COLS.INTERACTIONDATEISOUTC, days_considered_recent)


def filter_interactions_before(interactions_df:pd.DataFrame, days:int) -> pd.DataFrame:
    return utils_for_dfs.filter_time_column_before(interactions_df, INTERACTIONS_COLS.INTERACTIONDATEISOUTC, {"days":-1*days})


def filter_recent_sessions(sessions_df:pd.DataFrame, days_considered_recent=14) -> pd.DataFrame:
    return filter_recent_records_on_column(sessions_df, SESSIONS_COLS.ISOUTCENDTIME, days_considered_recent)


def filter_sessions_before(sessions_df:pd.DataFrame, days:int) -> pd.DataFrame:
    return utils_for_dfs.filter_time_column_before(sessions_df, SESSIONS_COLS.ISOUTCENDTIME, {"days":-1*days})


def filter_recent_records_on_column(df:pd.DataFrame, column:str, days_considered_recent) -> pd.DataFrame:
    return utils_for_dfs.filter_time_column_after(df, column, {"days": -1*days_considered_recent})


def derive_count_of_hourly_logins(logins_df:pd.DataFrame) -> pd.DataFrame :
    return pd.concat([
        derive_user_hour_login_count_df(user_app_tuple, user_logins_df)
        for user_app_tuple, user_logins_df in append_hours_to_user_logins(logins_df).groupby(["user", "app"])
    ])


def derive_user_hour_login_count_df(user_app_tuple:Tuple, user_logins_df:pd.DataFrame):
    return user_logins_df.groupby("hour").size().reset_index().rename(columns={0:"logins"}).assign(
        user = user_app_tuple[0],
        app = user_app_tuple[1]
    )


def append_hours_to_user_logins(logins_df:pd.DataFrame):
    login_hours = list(map(derive_hour_from_date, logins_df["loggedIn"]))
    return logins_df.assign(
        hour=list(map(lambda x: x["hour"], login_hours)),
        hour_number=list(map(lambda x: x["hour_number"], login_hours)),
        timezone=list(map(lambda x: x["timezone"], login_hours))
    )


def derive_total_logins_on_specific_dates(user_app_tuple:List, user_sessions_df:pd.DataFrame):
    return pd.DataFrame([
        {
            DAILY_LOGIN_COUNTS_COL.PROFILEID: user_app_tuple[0],
            DAILY_LOGIN_COUNTS_COL.APPID: user_app_tuple[1],
            DAILY_LOGIN_COUNTS_COL.DAY: date,
            DAILY_LOGIN_COUNTS_COL.TOTAL: count
        } for date, count in Counter(user_sessions_df[SESSIONS_COLS.ISOUTCSTARTTIME].map(derive_day_from_date)).items()
    ])


def expand_tag_column(df:pd.DataFrame, tag_column_name:str) -> pd.DataFrame:
    return df.assign(
        taggedConceptType=df[tag_column_name].map(lambda x: x.get("concept").get("context")),
        taggedConceptId=df[tag_column_name].map(lambda x: x.get("concept").get("id")),
        taggedConceptTitle=df[tag_column_name].map(lambda x: x.get("concept").get("title")),
        taggedConceptRelationship=df[tag_column_name].map(lambda x: x.get("relationship").get("id")),
        taggedOn=df[tag_column_name].map(lambda x: x.get("tagged"))
    )
