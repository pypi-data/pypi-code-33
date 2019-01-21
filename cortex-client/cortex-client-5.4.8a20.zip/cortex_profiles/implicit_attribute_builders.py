from typing import List

import pandas as pd
from cortex_profiles import utils
from cortex_profiles import implicit_attribute_builders, implicit_login_attribute_builders, implicit_insight_attribute_builders, implicit_attribute_builder_utils
from cortex_profiles.schemas.schemas import UNIVERSAL_ATTRIBUTES
from cortex_profiles.types.attributes import ProfileAttribute, AssignedProfileAttribute
from cortex_profiles.types.attribute_values import ListValue


def derive_attributes_from_timeranged_dataframes(timerange:str, insights_df: pd.DataFrame, interactions_df: pd.DataFrame, sessions_df: pd.DataFrame) -> List[ProfileAttribute]:
    return utils.flatten_list_recursively([
        implicit_insight_attribute_builders.derive_counter_attributes_for_count_of_specific_insight_interactions_per_insight_type(
            interactions_df, insights_df, timerange),
        implicit_insight_attribute_builders.derive_dimensional_attributes_for_count_of_specific_insight_interactions_per_encountered_tag(
            interactions_df, insights_df, timerange),
        implicit_insight_attribute_builders.derive_dimensional_attributes_for_total_duration_of_specific_insight_interactions_per_encountered_tag(
            interactions_df, insights_df, timerange),
        implicit_login_attribute_builders.derive_counter_attributes_for_specific_logins(sessions_df, timerange),
        implicit_login_attribute_builders.derive_counter_attributes_for_login_durations(sessions_df, timerange),
        implicit_login_attribute_builders.derive_dimensional_attributes_for_daily_login_counts(sessions_df, timerange),
        implicit_login_attribute_builders.derive_dimensional_attributes_for_daily_login_durations(sessions_df, timerange),
        implicit_login_attribute_builders.derive_average_attributes_for_daily_login_counts(sessions_df, timerange),
        implicit_login_attribute_builders.derive_average_attributes_for_daily_login_duration(sessions_df, timerange)
    ])


def derive_implicit_attributes(insights_df: pd.DataFrame, interactions_df: pd.DataFrame, sessions_df: pd.DataFrame, days_considered_recent:int=3) -> List[ProfileAttribute]:
    recent_insights_df, recent_interactions_df, recent_sessions_df = (
        implicit_attribute_builder_utils.filter_recent_insights(insights_df, days_considered_recent),
        implicit_attribute_builder_utils.filter_recent_interactions(interactions_df, days_considered_recent),
        implicit_attribute_builder_utils.filter_recent_sessions(sessions_df, days_considered_recent)
    )
    eternal_attributes = implicit_attribute_builders.derive_attributes_from_timeranged_dataframes(
        "eternally", insights_df, interactions_df, sessions_df
    )
    recent_attributes = implicit_attribute_builders.derive_attributes_from_timeranged_dataframes(
        "recently", recent_insights_df, recent_interactions_df, recent_sessions_df
    )
    return utils.flatten_list_recursively([eternal_attributes] + [recent_attributes])


def derive_profile_type_attribute(profileId:str, profileTypes:List[str]):
    return AssignedProfileAttribute(
        profileId = profileId,
        attributeKey = UNIVERSAL_ATTRIBUTES.TYPES,
        attributeValue = ListValue(profileTypes)
    )