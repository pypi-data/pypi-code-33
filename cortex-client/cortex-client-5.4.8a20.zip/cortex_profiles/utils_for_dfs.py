import json
from typing import List, TypeVar, Any, Tuple

import arrow
import pandas as pd
import attr

from . import utils

T = TypeVar("T")


def list_of_attrs_to_df(l:List) -> pd.DataFrame:
    return pd.DataFrame([
        attr.asdict(x) for x in l
    ])


def map_column(column: pd.Series, mapper:callable) -> pd.Series:
    return column.map(mapper)


def df_to_typed_list(df:pd.DataFrame, t:T) -> List[T]:
    return list(map(
        lambda rec: t(**rec),
        df.to_dict(orient="records")
    ))


def append_seconds_to_df(df:pd.DataFrame, column_name_to_append:str, start_time_col:str, end_time_col:str) -> pd.DataFrame:
    return df.assign(**{
        column_name_to_append: list(map(
            lambda x: utils.seconds_between_times(arrow.get(x[0]), arrow.get(x[1])),
            df[[start_time_col, end_time_col]].itertuples(index=False, name=None)
        ))
    })


def split_df_into_files_based_on_date(df: pd.DataFrame, on_date: str, file_pattern: str) -> None:
    """
    :param df: Dataframe to split
    :param on_date: Date column to split on
    :param file_pattern: The pattern to save the new files created, where {date} will be replaced with the actual date ...
    :return: Nothing, this function creates new files ...
    """
    for date, df_on_date in df.groupby(on_date):
        df_on_date.reset_index().to_csv(file_pattern.format(date=str(arrow.get(date).date())))


def explode_column(unindexed_df:pd.DataFrame, column:str) -> pd.DataFrame:
    """
    Assumption is df has no index ...
    :param df:
    :param column:
    :return:
    """
    if unindexed_df.empty:
        return unindexed_df
    id_columns = list(set(unindexed_df.columns).difference(set([column])))
    df = (unindexed_df.set_index(id_columns))[column].apply(pd.Series).stack().to_frame(column)
    for column in id_columns:
        df = df.reset_index(level=column)
    return df.reset_index(drop=True)


def records(df:pd.DataFrame) -> List[dict]:
    return df.to_dict(orient="records")


def head_as_dict(df:pd.DataFrame) -> str:
    return {} if df.empty else df.to_dict(orient="records")[0]


def filter_time_column_after(df:pd.DataFrame, time_column:str, shifter:dict) -> pd.DataFrame:
    """

    :param df: The dataframe to filter
    :param time_column: The name of the time column to filter
    :param shifter: Arrow friendly dict to shift an arrow time ...
    :return:
    """
    return df[df[time_column].map(arrow.get) >= arrow.utcnow().shift(**shifter)].reset_index(drop=True)


def filter_time_column_before(df:pd.DataFrame, time_column:str, shifter:dict) -> pd.DataFrame:
    """

    :param df: The dataframe to filter
    :param time_column: The name of the time column to filter
    :param shifter: Arrow friendly dict to shift an arrow time ...
    :return:
    """
    return df[df[time_column].map(arrow.get) <= arrow.utcnow().shift(**shifter)].reset_index(drop=True)


def df_to_tuples(df:pd.DataFrame, columns:List):
    return utils.tuples_with_nans_to_tuples_with_nones(df[columns].itertuples(index=False, name=None))


def parse_set_notation(string_series:pd.Series) -> pd.Series:
    if string_series.empty:
        return pd.Series([])
    return string_series.map(parse_string_set_notation)

def parse_string_set_notation(string:str) -> pd.Series:
    return set(string[1:-1].split(","))

def parse_set_of_json_strings_notation(string_series):
    if string_series.empty:
        return []
    return string_series.map(
        utils.first_arg_is_type_wrapper(
            lambda string: list(map(
                lambda x: json.loads(x),
                json.loads("[{}]".format(string[1:-1]))
            )),
            (str)
        )
    )


def df_to_records(df:pd.DataFrame) -> List[dict]:
    return df.to_dict('records')


# @utils.timeit
# def publish_df_to_collection(df, col):
#     if not df.empty:
#         return col.insert_many(df.to_dict('records'))
#     else:
#         print("DataFrame empty, nothing to publish ...")
#
#
# @utils.timeit
# def upsert_df_to_collection(df, col, identifiers):
#     id_mapper = lambda r: {x: r[x] for x in identifiers}
#     if not df.empty:
#         requests = map(lambda x: ReplaceOne(id_mapper(x), x, upsert=True), df.to_dict('records'))
#         try:
#             results = col.bulk_write(list(requests), ordered=False)
#             return results.bulk_api_result["nUpserted"]
#         except BulkWriteError as bwe:
#             print("Error Upserting Records: !! {}".format(bwe.details))
#             return bwe.details["nUpserted"]
#     else:
#         print("DataFrame empty, nothing to publish ...")
#         return 0



def merge_list_of_dfs_similarly(group_list:List[pd.DataFrame], **kwargs) -> pd.DataFrame:
    """
    Merged a list of dataframes ... into a single dataframe ... on the same criteria ...
    :param group_list:
    :param kwargs:
    :return:
    """
    if len(group_list) == 0:
        return pd.DataFrame(columns=[kwargs.get("on", kwargs.get("left_on"))])
    if len(group_list) == 1:
        return group_list[0]
    if len(group_list) == 2:
        return pd.merge(group_list[0], group_list[1], **kwargs)
    if len(group_list) >= 3:
        return merge_list_of_dfs_similarly(
            [merge_list_of_dfs_similarly(group_list[:2], **kwargs)] + group_list[2:]
        )

def split_list_of_tuples(l:List[Tuple[Any,Any]]) -> Tuple[List[Any], List[Any]] :
    """
    NOTE: No python way of specifying that the return type ... the number of List[Any] in it depends on the size of the tuple passed in ...
    :param l:
    :return:
    """
    if not l:
        return l
    lengths_of_each_tuple = map(lambda x: len(list(x)), l)
    all_tuples_same_length =  all(lambda x: x == lengths_of_each_tuple[0], lengths_of_each_tuple)
    assert all_tuples_same_length, "All tuples must be of the same length: {}".format(lengths_of_each_tuple[0])
    return tuple(*[[tupe[i] for tupe in l] for i in range(0, lengths_of_each_tuple[0])])
