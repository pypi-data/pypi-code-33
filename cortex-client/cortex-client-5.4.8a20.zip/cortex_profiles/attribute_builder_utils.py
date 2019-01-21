import uuid
from typing import List, Optional, Mapping, Any

import attr
import pandas as pd
import pydash
from cortex_profiles import utils, utils_for_dfs
from cortex_profiles.types.attribute_values import PrimitiveValue, DimensionalAttributeContent, Dimension
from cortex_profiles.types.attributes import ObservedProfileAttribute, DeclaredProfileAttribute


def derive_dimensional_observed_attributes_from_df(
        df:pd.DataFrame,
        attribute_identifiers:List[str],
        attributeKeyPattern:str,
        dimensionIDColumn:str,
        dimensionValueColumn:str,
        contextOfDimension:str,
        classOfDimensionValue:str,
        isColumnForDimensionContext:bool=True,
        additional_identifiers:Optional[dict]=None
    ) -> List[ObservedProfileAttribute]:
    return [
        derive_observed_dimensional_attributes_from_grouped_df(
            gdf,
            attribute_identifiers,
            list(gid),
            attributeKeyPattern,
            dimensionIDColumn,
            dimensionValueColumn,
            contextOfDimension,
            classOfDimensionValue,
            isColumnForDimensionContext,
            additional_identifiers)
        for gid, gdf in df.groupby(attribute_identifiers, as_index=False)
    ]


def derive_observed_dimensional_attributes_from_grouped_df(
        grouped_df:pd.DataFrame,
        group_id_keys:List[str],
        group_id_values:List[Any],
        attributeKeyPattern:str,
        dimensionIDColumn:str,
        dimensionValueColumn:str,
        contextOfDimension:str,
        classOfDimensionValue:str,
        isColumnForDimensionContext:bool=False,
        additional_identifiers:Optional[dict]=None
    ) -> ObservedProfileAttribute:
    if grouped_df.empty:
        return None
    assert "profileId" in grouped_df.columns, "ProfileId must be in dataframe ..."
    identifier = dict(zip(group_id_keys, group_id_values))
    identifier = identifier if not additional_identifiers else pydash.merge(identifier, additional_identifiers)
    attributeValue = DimensionalAttributeContent(
        contextOfDimension=identifier[contextOfDimension] if isColumnForDimensionContext else contextOfDimension,
        contextOfDimensionValue=attr.fields(classOfDimensionValue).context.default,
        value=list(sorted(
            [
                Dimension(dimensionId=x, dimensionValue=y)
                for x, y in utils_for_dfs.df_to_tuples(grouped_df, [dimensionIDColumn, dimensionValueColumn])
            ],
            key=lambda d: -1 * d.dimensionValue
        ))
    )
    return ObservedProfileAttribute(
        id=str(uuid.uuid4()),
        attributeKey=attributeKeyPattern.format(**identifier),
        profileId=str(identifier["profileId"]),
        createdAt=utils.utc_timestamp(),
        attributeValue=attributeValue,
    )


def derive_simple_observed_attributes_from_df(
        df:pd.DataFrame,
        attribute_identifiers:List[str],
        attributeKeyPattern:str,
        valueColumn:str,
        classOfValue:type,
        additional_identifiers:Optional[Mapping[str, str]]=None
    ) -> List[ObservedProfileAttribute]:
    return [
        derive_simple_observed_attributes_from_grouped_df(
            gdf, attribute_identifiers, list(gid), attributeKeyPattern,
            valueColumn, classOfValue, additional_identifiers)
        for gid, gdf in df.groupby(attribute_identifiers, as_index=False)
    ]


def derive_simple_observed_attributes_from_grouped_df(
        grouped_df:pd.DataFrame,
        group_id_keys:List[str],
        group_id_values:List[Any],
        attributeKeyPattern:str,
        counterColumn:str,
        classOfValue:type,
        additional_identifiers:Optional[Mapping[str, str]]=None
    ) -> ObservedProfileAttribute:
    if grouped_df.empty:
        return []
    assert "profileId" in grouped_df.columns, "profileId must be a column in the dataframe ..."
    identifier = dict(zip(group_id_keys, group_id_values))
    identifier = identifier if not additional_identifiers else pydash.merge(identifier, additional_identifiers)
    attributeValue = classOfValue(
        value=sum(grouped_df[counterColumn])
    )
    return ObservedProfileAttribute(
        id=utils.unique_id(),
        attributeKey=attributeKeyPattern.format(**identifier),
        profileId=str(identifier["profileId"]),
        createdAt=utils.utc_timestamp(),
        attributeValue=attributeValue,
    )


def derive_declared_attributes_from_key_value_df(
        declarations:pd.DataFrame,
        profileIdColumn:str="profileId",
        keyColumn:str="key",
        valueColumn:str="value",
        attributeValueClass:type=PrimitiveValue
    ) -> List[DeclaredProfileAttribute]:
    return [
        DeclaredProfileAttribute(
            id=utils.unique_id(),
            attributeKey=rec[keyColumn],
            profileId=str(rec[profileIdColumn]),
            createdAt=utils.utc_timestamp(),
            attributeValue=attributeValueClass(rec[valueColumn]),
        )
        for rec in utils_for_dfs.df_to_records(declarations)
    ]

def derive_declared_attributes_from_value_only_df(
        declarations:pd.DataFrame,
        profileIdColumn:str="profileId",
        key:str="key",
        valueColumn:str="value",
        attributeValueClass:type=PrimitiveValue
    ) -> List[DeclaredProfileAttribute]:
    return [
        DeclaredProfileAttribute(
            id=utils.unique_id(),
            attributeKey=key,
            profileId=str(rec[profileIdColumn]),
            createdAt=utils.utc_timestamp(),
            attributeValue=attributeValueClass(rec[valueColumn]),
        )
        for rec in utils_for_dfs.df_to_records(declarations)
    ]



def derive_quantile_config_for_column(df:pd.DataFrame, column_name:str, quantile_config:dict) -> pd.Series:
    return {
        key: list(map(lambda x: df[column_name].quantile(x), values)) for key, values in quantile_config.items()
    }


def determine_bucket_from_quartile_config(value:object, config:dict) -> str:
    # Taking tail for values on the edge to be more generous
    return [key for key, values in config.items() if (value >= values[0] and value <= values[1])][-1]


def high_med_low_bucket(df:pd.DataFrame, column_name:str, quantile_config:dict) -> pd.Series:
    return df[column_name].map(lambda x: determine_bucket_from_quartile_config(x, quantile_config))