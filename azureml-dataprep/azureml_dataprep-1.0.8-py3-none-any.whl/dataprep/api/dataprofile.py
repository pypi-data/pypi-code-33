# Copyright (c) Microsoft Corporation. All rights reserved.
"""Classes for collecting summary statistics on the data produced by a Dataflow."""
from collections import namedtuple, OrderedDict
from typing import Any, Dict, List
from .engineapi.api import EngineAPI
from .engineapi.typedefinitions import ActivityReference, DataField, ExecuteInspectorCommonArguments, FieldType, InspectorArguments
from .value import value_from_field

_MAX_ROW_COUNT = 2**31 - 1

ValueCountEntry = namedtuple('ValueCountEntry', ['value', 'count'])
HistogramBucket = namedtuple('HistogramBucket', ['lower_bound', 'upper_bound', 'count'])
TypeCountEntry = namedtuple('TypeCountEntry', ['type', 'count'])

class DTypes(Dict):
    def __init__(self, dict):
        super().__init__(dict)

    def __repr__(self):
        column_types = ["""{0!s:<25}{1!s:<16}""".format(column, dtype, end=' ') for (column, dtype) in self.items()]
        return '\n'.join(column_types)
        

class DataProfile:
    """
    A DataProfile collects summary statistics on the data produced by a Dataflow.

    :var columns: Profile information for each result column.
    :vartype columns: Dict[str, ColumnProfile]
    """

    def __init__(self, engine_api: EngineAPI, context: ActivityReference):
        self._engine_api = engine_api
        self._context = context

        table_inspector = self._engine_api.execute_inspector(ExecuteInspectorCommonArguments(
            context=self._context,
            inspector_arguments=InspectorArguments(inspector_type='Microsoft.DPrep.TableInspector', arguments={}),
            offset=0,
            row_count=_MAX_ROW_COUNT))
        column_names = [column_definition.id for column_definition in table_inspector.column_definitions]
        rows = table_inspector.rows_data.rows

        def values_for_column(fields):
            return {
                name: value_from_field(field)
                for name, field in zip(column_names, fields)
                if field is not None and field.type != FieldType.NULL and field.type != FieldType.ERROR
            }

        self.columns = OrderedDict([(row[0].value, ColumnProfile(values_for_column(row))) for row in rows])

    @property
    def dtypes(self) -> Dict[str, FieldType]:
        """
        Column data types.

        :return: A dictionary, where key is the column name and value is :class:`azureml.dataprep.FieldType`.
        """
        return DTypes({column: column_profile.type for (column, column_profile) in self.columns.items()})

    @property
    def row_count(self) -> int:
        """
        Count of rows in this DataProfile.

        :return: Count of rows.
        :rtype: int
        """
        for column_profile in self.columns.values():
            # return count of rows from first column profile we iterate over.
            return int(column_profile.count)

    def _repr_html_(self):
        """
        HTML representation for IPython.
        """
        try:
            import pandas as pd
        except ImportError:
            return None

        stats = [column_profile.get_stats() for column_profile in self.columns.values()]
        return pd.DataFrame(stats, index=self.columns.keys(), columns=ColumnProfile.STAT_COLUMNS).to_html()

    def __repr__(self):
        return '\n'.join(map(str, self.columns.values()))


class ColumnProfile:
    """
    A ColumnProfile collects summary statistics on a particular column of data produced by a Dataflow.

    :var name: Name of column
    :vartype name: str
    :var type: Type of values in column
    :vartype type: FieldType

    :var min: Minimum value
    :vartype min: Any
    :var max: Maximum value
    :vartype max: Any
    :var count: Count of rows
    :vartype count: int
    :var missing_count: Count of rows with a missing value
    :vartype missing_count: int
    :var not_missing_count: Count of rows with a value
    :vartype not_missing_count: int
    :var error_count: Count of rows with an error value
    :vartype error_count: int
    :var percent_missing: Percent of the values that are missing
    :vartype percent_missing: double
    :var empty_count: Count of rows with empty string value
    :vartype empty_count: int

    :var lower_quartile: Estimated 25th-percentile value
    :vartype lower_quartile: double
    :var median: Estimated median value
    :vartype median: double
    :var upper_quartile: Estimated 75th-percentile value
    :vartype upper_quartile: double
    :var mean: Mean
    :vartype mean: double
    :var std: Standard deviation
    :vartype std: double
    :var variance: Variance
    :vartype variance: double
    :var skewness: Skewness
    :vartype skewness: double
    :var kurtosis: Kurtosis
    :vartype kurtosis: double
    :var quantiles: Dictionary of quantiles
    :vartype quantiles: Dict[double, double]

    :var value_counts: Counts of discrete values in the data; None if too many values.
    :vartype value_counts: List[ValueCountEntry]
    :var histogram: Histogram buckets showing the distribution of the data; None if data is non-numeric.
    :vartype histogram: List[HistogramBucket]
    """
    def __init__(self, values: Dict[str, Any]):
        self.name = values.get('Column')
        self.type = FieldType(values.get('type'))

        self.min = values.get('min')
        self.max = values.get('max')
        self.count = values.get('count')
        self.missing_count = values.get('num_missing')
        self.not_missing_count = values.get('num_not_missing')
        self.percent_missing = values.get('%missing')
        self.error_count = values.get('num_errors')
        self.empty_count = values.get('num_empty')

        self.value_counts = self._prepare_value_counts(values.get('value_count'))

        # Present for numeric columns only, will otherwise be None.
        self.lower_quartile = values.get('25%')
        self.median = values.get('50%')
        self.upper_quartile = values.get('75%')
        self.mean = values.get('mean')
        self.std = values.get('standard_deviation')
        self.variance = values.get('variance')
        self.skewness = values.get('skewness')
        self.kurtosis = values.get('kurtosis')
        self.histogram = self._prepare_histogram(values.get('histogram'))
        self.quantiles = OrderedDict([
            (0.001, values.get('0.1%')),
            (0.01, values.get('1%')),
            (0.05, values.get('5%')),
            (0.25, values.get('25%')),
            (0.50, values.get('50%')),
            (0.75, values.get('75%')),
            (0.95, values.get('95%')),
            (0.99, values.get('99%')),
            (0.999, values.get('99.9%'))])

        self.type_counts = self._prepare_type_counts(values.get('type_count'))

    @property
    def _is_numeric(self):
        return self.type == FieldType.INTEGER or self.type == FieldType.DECIMAL

    def _prepare_value_counts(self, entries: List[Any]):
        if entries and len(entries) > 0:
            def process_entry(entry):
                value = value_from_field(DataField.from_pod(entry['value']))
                count = int(entry['count'])
                return ValueCountEntry(value, count)
            return [ process_entry(entry) for entry in entries ]
        return None

    def _prepare_histogram(self, fields: List[Dict[str, Any]]):
        if fields:
            values = (f['value'] for f in fields)
            def generate_buckets():
                last_position = None
                for position, count in zip(values, values):
                    if last_position is not None:
                        yield HistogramBucket(lower_bound=last_position, upper_bound=position, count=count)
                    last_position = position
            histogram = list(generate_buckets())
            if len(histogram) > 0:
                return histogram
        return None

    def _prepare_type_counts(self, entries: List[Any]):
        return [TypeCountEntry(FieldType(entry['type']), count = int(entry['count'])) for entry in entries]

    def get_stats(self):
        return [
            self.type, self.min, self.max, self.count, self.missing_count, self.not_missing_count, self.percent_missing,
            self.error_count, self.empty_count,
            self.quantiles[0.001] if self._is_numeric else '',
            self.quantiles[0.01] if self._is_numeric else '',
            self.quantiles[0.05] if self._is_numeric else '',
            self.quantiles[0.25] if self._is_numeric else '',
            self.quantiles[0.50] if self._is_numeric else '',
            self.quantiles[0.75] if self._is_numeric else '',
            self.quantiles[0.95] if self._is_numeric else '',
            self.quantiles[0.99] if self._is_numeric else '',
            self.quantiles[0.999] if self._is_numeric else '',
            self.mean if self._is_numeric else '',
            self.std if self._is_numeric else '',
            self.variance if self._is_numeric else '',
            self.skewness if self._is_numeric else '',
            self.kurtosis if self._is_numeric else ''
        ]

    STAT_COLUMNS = [
        'Type', 'Min', 'Max', 'Count', 'Missing Count', 'Not Missing Count', 'Percent missing', 'Error Count',
        'Empty count', '0.1% Quantile', '1% Quantile', '5% Quantile', '25% Quantile', '50% Quantile', '75% Quantile',
        '95% Quantile', '99% Quantile', '99.9% Quantile', 'Mean', 'Standard Deviation', 'Variance', 'Skewness', 'Kurtosis'
    ]

    def _repr_html_(self):
        """
        HTML representation for IPython.
        """
        try:
            import pandas as pd
        except ImportError:
            return None
        return pd.DataFrame(self.get_stats(), index=ColumnProfile.STAT_COLUMNS, columns=['Statistics']).to_html()

    def __repr__(self):
        result = """\
ColumnProfile
    name: {name}
    type: {type}

    min: {min}
    max: {max}
    count: {count}
    missing_count: {missing_count}
    not_missing_count: {not_missing_count}
    percent_missing: {percent_missing}
    error_count: {error_count}
    empty_count: {empty_count}

""".format(**vars(self))

        if self._is_numeric:
            result += """\

    Quantiles:
         0.1%: {0!s}
           1%: {1!s}
           5%: {2!s}
          25%: {3!s}
          50%: {4!s}
          75%: {5!s}
          95%: {6!s}
          99%: {7!s}
        99.9%: {8!s}

    mean: {9!s}
    std: {10!s}
    variance: {11!s}
    skewness: {12!s}
    kurtosis: {13!s} 
""".format(self.quantiles[0.001],
           self.quantiles[0.01],
           self.quantiles[0.05],
           self.quantiles[0.25],
           self.quantiles[0.50],
           self.quantiles[0.75],
           self.quantiles[0.95],
           self.quantiles[0.99],
           self.quantiles[0.999],
           self.mean,
           self.std,
           self.variance,
           self.skewness,
           self.kurtosis)

        return result
