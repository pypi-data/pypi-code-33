
import copy
from typing import List, Tuple

import arrow
import pandas as pd

from . import utils
from . import utils_for_dfs
from cortex_profiles.schemas.schemas import CONTEXTS
from cortex_profiles.schemas.dataframes import SESSIONS_COLS, INSIGHT_ACTIVITY_COLS


def associate_activity_with_sessions(activity_df:pd.DataFrame, sessions_df:pd.DataFrame) -> pd.DataFrame:
    sessions_df = sessions_df.assign(**{
        SESSIONS_COLS.ISOUTCSTARTTIME:sessions_df[SESSIONS_COLS.ISOUTCSTARTTIME].map(arrow.get),
        SESSIONS_COLS.ISOUTCENDTIME:sessions_df[SESSIONS_COLS.ISOUTCENDTIME].map(arrow.get)
    })
    return activity_df[INSIGHT_ACTIVITY_COLS.ACTIVITY_TIME].map(arrow.get).map(
        lambda x: utils_for_dfs.head_as_dict(
            sessions_df[
                (sessions_df[SESSIONS_COLS.ISOUTCSTARTTIME].map(lambda y: x >= y)) &
                (sessions_df[SESSIONS_COLS.ISOUTCENDTIME].map(lambda y: x <= y))
                ]
        ).get(SESSIONS_COLS.ID)
    )


def derive_sessions_from_user_activity_df(user_activity_df: pd.DataFrame) -> pd.DataFrame:
    sessions_df = pd.concat(
        [
            derive_sessions_from_user_app_specific_activity(user, udf)
            for user, udf in user_activity_df.groupby(by=[INSIGHT_ACTIVITY_COLS.PROFILEID, INSIGHT_ACTIVITY_COLS.APPID])
        ],
        ignore_index=True
    )
    return sessions_df


def derive_sessions_from_user_app_specific_activity(profile_app_tuple:str, user_app_specific_activity_df:pd.DataFrame) -> pd.DataFrame:
    profileId, appId = profile_app_tuple
    df = compute_sessions_times_from_activity_df(
        user_app_specific_activity_df[[INSIGHT_ACTIVITY_COLS.ISOUTCSTARTTIME, INSIGHT_ACTIVITY_COLS.ISOUTCENDTIME]].itertuples(index=False, name=None)
    )
    return df.assign(**{
        SESSIONS_COLS.CONTEXT: CONTEXTS.SESSION,
        SESSIONS_COLS.ID:[utils.unique_id() for x in range(0, df.shape[0])],
        SESSIONS_COLS.PROFILEID:profileId,
        SESSIONS_COLS.APPID:appId,
        SESSIONS_COLS.ISOUTCSTARTTIME:df[SESSIONS_COLS.ISOUTCSTARTTIME].map(str),
        SESSIONS_COLS.ISOUTCENDTIME:df[SESSIONS_COLS.ISOUTCENDTIME].map(str),
        SESSIONS_COLS.DURATIONINSECONDS:df[[SESSIONS_COLS.ISOUTCSTARTTIME, SESSIONS_COLS.ISOUTCENDTIME]].apply(add_duration_to_login_time, axis=1)
    })


def fold_start_and_stop_time_tuples_into_dict(startTime_stopTime_tuples:List[Tuple]) -> dict:
    d = {}
    for start_time, stop_time in startTime_stopTime_tuples:
        if start_time in d:
            # Take the newer stop time ...
            if stop_time > d[start_time]:
                d[start_time] = stop_time
        else:
            d[start_time] = stop_time
    return d


def compute_sessions_times_from_activity_df(startTime_stopTime_tuples:List[Tuple], session_threshold_mins:int=30) -> pd.DataFrame:
    """
    Key of the dict is when an activity started, value is when it ended ...
    For every start time ...
        is there another start time that is less than 30mins newer then it?
            if so, make the latest end time end time for the earlier start time and get rid of this row?
    """
    sessions = fold_start_and_stop_time_tuples_into_dict(
        map(lambda x: (arrow.get(x[0]), arrow.get(x[1])), startTime_stopTime_tuples)
    )
    for start_time, end_time in copy.deepcopy(sessions).items():
        if start_time not in sessions:
            # Skip whatever has been taken care of ...
            continue

        start_times_within_session_threshold = list(map(
            lambda x: x[0],
            search_for_values_in_list(
                sessions.items(),
                lambda start_time_end_time_tuple: (
                    time_is_within(start_time_end_time_tuple[0], start_time, dict(minutes=session_threshold_mins)) or
                    time_is_within(start_time_end_time_tuple[1], start_time, dict(minutes=session_threshold_mins))
                )
            )
        ))

        all_start_times = start_times_within_session_threshold + [start_time]
        all_end_times = [sessions[x] for x in start_times_within_session_threshold] + [end_time]
        # Find the oldest start time
        oldest_start_time = oldest(all_start_times)
        # Find the newest end time
        newest_end_time = newest(all_end_times)
        # Remove all of the start times involved in these queries ...
        for x in all_start_times:
            if x in sessions:
                del sessions[x]
        # Set the oldest start time with the newest end time ...
        sessions[oldest_start_time] = newest_end_time
    return pd.DataFrame([
        {SESSIONS_COLS.ISOUTCSTARTTIME: start_time, SESSIONS_COLS.ISOUTCENDTIME: end_time} for start_time, end_time in sessions.items()
    ])


def add_duration_to_login_time(startTime_endTime_tuple):
    return abs(startTime_endTime_tuple[0].float_timestamp - startTime_endTime_tuple[1].float_timestamp)


def oldest(list_of_times:List) -> object:
    if not list_of_times:
        return None
    return sorted(list_of_times, key=lambda x: x)[0]


def newest(list_of_times:List) -> object:
    if not list_of_times:
        return None
    return sorted(list_of_times, key=lambda x: x)[-1]


def invert_dict(d:dict) -> dict:
    return {
        k: -1 * v for k, v in d.items()
    }

def time_is_within(time_to_check, time_to_shift, time_shifter):
    """
    Before and after ...
    :param time_to_check:
    :param time_to_shift:
    :param time_shifter:
    :return:
    """
    return (
        (
            time_to_check >= time_to_shift.shift(**invert_dict(time_shifter)) and time_to_check < time_to_shift
        )
        or
        (
            time_to_check < time_to_shift.shift(**time_shifter) and time_to_check >= time_to_shift
        )
    )


def search_for_values_in_list(list_to_search:List, search_query:callable) -> List:
    return list(filter(search_query, list_to_search))


def convert_to_string_dict(d:dict) -> dict:
    return {str(k): str(v) for k, v in d.items()}

