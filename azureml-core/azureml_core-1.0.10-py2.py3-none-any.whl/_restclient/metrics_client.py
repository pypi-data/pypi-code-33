# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Access metrics client"""
import logging
import os
import six
import sys

from azureml.exceptions import AzureMLException
from azureml._logging import START_MSG, STOP_MSG
from azureml._async import TaskQueue, BatchTaskQueue

from .contracts.utils import get_new_id, get_timestamp
from .models.metric_schema_dto import MetricSchemaDto
from .models.metric_schema_property_dto import MetricSchemaPropertyDto
from .models.run_metric_dto import RunMetricDto
from .run_client import RunClient
from .models.metric_dto import MetricDto
from .models.batch_metric_dto import BatchMetricDto

module_logger = logging.getLogger(__name__)

AZUREML_BOOL_METRIC_TYPE = "bool"
AZUREML_FLOAT_METRIC_TYPE = "float"
AZUREML_INT_METRIC_TYPE = "int"
AZUREML_NULL_METRIC_TYPE = "none"
AZUREML_STRING_METRIC_TYPE = "string"

AZUREML_IMAGE_METRIC_TYPE = "azureml.v1.image"
AZUREML_LIST_METRIC_TYPE = "azureml.v1.list"
AZUREML_SCALAR_METRIC_TYPE = "azureml.v1.scalar"
AZUREML_TABLE_METRIC_TYPE = "azureml.v1.table"
AZUREML_CONFUSION_MATRIX_METRIC_TYPE = "azureml.v1.confusion_matrix"
AZUREML_ACCURACY_TABLE_METRIC_TYPE = "azureml.v1.accuracy_table"
AZUREML_RESIDUALS_METRIC_TYPE = "azureml.v1.residuals"
AZUREML_PREDICTIONS_METRIC_TYPE = "azureml.v1.predictions"

AZUREML_METRICS_CLIENT_BATCH_SIZE_ENV_VAR = "AZUREML_METRICS_BATCH_SIZE"
AZUREML_METRICS_CLIENT_BATCH_CUSHION_ENV_VAR = "AZUREML_METRICS_BATCH_CUSHION"
AZUREML_METRICS_CLIENT_POLLING_INTERVAL_ENV_VAR = "AZUREML_METRICS_POLLING_INTERVAL"

AZUREML_MAX_NUMBER_SIZE_IN_BITS = 64
AZUREML_MAX_NUMBER_METRICS_BATCH = 50
AZUREML_METRICS_CLIENT_BATCH_CUSHION = 5
AZUREML_METRICS_CLIENT_MIN_POLLING_INTERVAL = 1  # Minimum supported interval


class MetricsClient(RunClient):
    """Metrics client class"""
    _type_to_metric_type = {float: AZUREML_FLOAT_METRIC_TYPE,
                            str: AZUREML_STRING_METRIC_TYPE,
                            bool: AZUREML_BOOL_METRIC_TYPE,
                            type(None): AZUREML_NULL_METRIC_TYPE}

    for integer_type in six.integer_types:
        _type_to_metric_type[integer_type] = AZUREML_INT_METRIC_TYPE

    _type_to_converter = {}
    try:
        import numpy as np

        # Add boolean type support
        _type_to_converter[np.bool_] = bool

        # Add str type support
        _type_to_converter[np.unicode_] = str

        # Add int type support
        numpy_ints = [np.int0, np.int8, np.int16, np.int16, np.int32]
        numpy_unsigned_ints = [np.uint0, np.uint8, np.uint8, np.uint16, np.uint32]

        for numpy_int_type in numpy_ints + numpy_unsigned_ints:
            _type_to_converter[numpy_int_type] = int

        # Add float type support
        numpy_floats = [np.float16, np.float32, np.float64]

        for numpy_float_type in numpy_floats:
            _type_to_converter[numpy_float_type] = float

        try:
            # Support large float as string
            _type_to_converter[np.float128] = repr
        except AttributeError as attribute_error:
            module_logger.debug("numpy.float128 is unsupported, expected for windows")
    except ImportError as import_error:
        module_logger.debug("Unable to import numpy, numpy typed metrics unsupported")

    def __init__(self, *args, **kwargs):
        self._use_batch = kwargs.pop("use_batch", True)
        super(MetricsClient, self).__init__(*args, **kwargs)
        if self._use_batch:
            max_batch_size = int(os.environ.get(AZUREML_METRICS_CLIENT_BATCH_SIZE_ENV_VAR,
                                                AZUREML_MAX_NUMBER_METRICS_BATCH))
            batch_cushion = int(os.environ.get(AZUREML_METRICS_CLIENT_BATCH_CUSHION_ENV_VAR,
                                               AZUREML_METRICS_CLIENT_BATCH_CUSHION))
            interval = int(os.environ.get(AZUREML_METRICS_CLIENT_POLLING_INTERVAL_ENV_VAR,
                                          AZUREML_METRICS_CLIENT_MIN_POLLING_INTERVAL))
            self._logger.debug(
                "Overrides: Max batch size: {0}, batch cushiion: {1}, Interval: {2}.".format(
                    max_batch_size, batch_cushion, interval))

            self._task_queue = BatchTaskQueue(self._log_batch,
                                              worker_pool=self._pool,
                                              interval=interval,
                                              max_batch_size=max_batch_size,
                                              batch_cushion=batch_cushion,
                                              _ident="PostMetricsBatch",
                                              _parent_logger=self._logger)
        else:
            self._task_queue = TaskQueue(worker_pool=self._pool,
                                         _ident="PostMetricsSingle",
                                         _parent_logger=self._logger)

        self._logger.debug("Used {} for use_batch={}.".format(type(self._task_queue), self._use_batch))

    @classmethod
    def get_converted_value(cls, value):
        """return supported metrics value, otherwise, convert to string"""
        value_type = type(value)
        if value_type in cls._type_to_metric_type:
            return value
        else:
            converter = cls._type_to_converter.get(value_type, repr)
            return converter(value)

    @classmethod
    def to_cells(cls, keys, values):
        """return metrics cell as list of dictionary"""
        cells = []
        seen_keys = set()
        message = ""
        warning_message = ""
        for key, value in zip(keys, values):
            converted_value = cls.get_converted_value(value)
            if key not in seen_keys and type(value) != type(converted_value):
                message_line = "Converted key {0} of value {1} to {2}.\n".format(
                    key, value, converted_value)
                if not isinstance(value, str) and isinstance(converted_value, str):
                    warning_message += message_line
                else:
                    message += message_line
                seen_keys.add(key)
            cells.append({key: converted_value})

        if message:
            module_logger.debug(message)
        if warning_message:
            module_logger.warning(warning_message)
        return cells

    @classmethod
    def add_cells(cls, name, out, table_cell_types, cells, cell_types):
        """add new cells"""
        for cell in cells:
            for key in cell:
                var = cell[key]
                cell_type = cell_types[key]
                if key not in table_cell_types:
                    table_cell_types = cell_types[key]

                if key in out:
                    out[key] = out[key] if isinstance(out[key], list) else [out[key]]

                if cell_type != table_cell_types[key]:
                    module_logger.debug("Invalid type for metric name {}, type: "
                                        "{}, expected: {} appending None instead.".format(name,
                                                                                          cell_type,
                                                                                          table_cell_types[key]))
                    out[key].append(None)
                elif key not in out:
                    if cell_type == AZUREML_FLOAT_METRIC_TYPE:
                        var = float(var)
                    out[key] = var
                else:
                    out[key].append(var)

    @classmethod
    def add_table(cls, name, out, table_column_types, cells, cell_types):
        """add a new table"""
        if name in out:
            table_out = out[name]
        else:
            out[name] = {}
            table_out = out[name]

        existing_columns = table_out.keys()

        # TODO find simpler way to do this
        table_length = 0
        for key in existing_columns:
            value = table_out[key]
            table_length = len(value) if isinstance(value, list) else 1
            break

        #  Fill new columns with None
        if table_length != 0:
            for col in cell_types:
                if col not in table_out:
                    table_out[col] = table_length * [None]

        #  Add column type for new columns to known
        for col in cell_types:
            if col not in table_column_types:
                table_column_types[col] = cell_types[col]

        table_to_add = {}
        cls.add_cells(name, table_to_add, table_column_types, cells, cell_types)

        #  Check for table size invariant, columns must be of the same length
        length = None
        for key in table_to_add:
            values = table_to_add[key]
            current_length = len(values) if isinstance(values, list) else 1
            if length is None:
                length = current_length
            else:
                if length != current_length:
                    module_logger.warning("Invalid table, mixmatched column sizes, column of length {} "
                                          ", expected length {}".format(current_length, length))

        #  Fill missing columns with None
        for col in existing_columns:
            if col not in table_to_add:
                table_to_add[col] = length * [None]

        #  Extend table out
        for key in table_to_add:
            to_add = table_to_add[key]
            if key not in table_out:
                table_out[key] = to_add
            elif isinstance(to_add, list):
                table_out[key].extend(to_add)
            else:
                table_out[key].append(to_add)

    @classmethod
    def add_metrics_func(cls, metric_type):
        """add metrics table or cells by type"""
        if metric_type == AZUREML_TABLE_METRIC_TYPE:
            return cls.add_table
        else:
            return cls.add_cells

    @classmethod
    def dto_to_metrics_dict(cls, metrics_dto):
        """convert metrics_dto to dictionary"""
        out = {}
        metric_types = {}
        original_cell_types = {}
        for metric in metrics_dto:
            name = metric.name
            metric_type = metric.metric_type
            schema = metric.schema
            cell_types = {prop.property_id: prop.type for prop in schema.properties}
            if name not in metric_types:
                metric_types[name] = metric_type
                original_cell_types[name] = cell_types

            if metric_types[name] == metric_type:
                cls.add_metrics_func(metric_type)(name, out, original_cell_types[name],
                                                  metric.cells, cell_types)
            else:
                module_logger.warning("Conflicting metric types, logged metric "
                                      "of type: {} to name: {}, expected metric "
                                      "type is {}".format(metric_type, name,
                                                          metric_types[name]))
        return out

    def get_all_metrics(self):
        """get all metrics with the same run_id"""
        expression = "{}{}".format("RunId eq ", self._run_id)
        if self.api_route == MetricsClient.OLD_ROUTE:
            func = self._client.legacy_runmetric.list
        else:
            func = self._client.run_metric.list
        metrics = self._execute_with_experiment_arguments(func,
                                                          filter=expression,
                                                          is_paginated=True)
        return metrics

    def get_all(self):
        metrics = self.get_all_metrics()
        return MetricsClient.dto_to_metrics_dict(metrics)

    @classmethod
    def create_run_metric_dto(cls, run_id, name, value,
                              data_location=None,
                              description="",
                              metric_type="vienna.custom"):
        """create a new run_metric Dto"""
        # Load cells and handle list vs non list cells
        num_cells, cells = (len(value), value) if isinstance(value, list) else (1, [value])
        seen = set()
        properties = []
        for cell in cells:
            for key in cell:
                if key not in seen:
                    val = cell[key]
                    properties.append(MetricsClient.get_value_property(name, val, key))
                    seen.add(key)

        metrics_schema_dto = MetricSchemaDto(num_properties=len(properties),
                                             properties=properties)
        run_metric_dto = RunMetricDto(run_id=run_id,
                                      metric_id=get_new_id(),
                                      metric_type=metric_type,
                                      created_utc=get_timestamp(),
                                      name=name,
                                      description=description,
                                      num_cells=num_cells,
                                      cells=cells,
                                      schema=metrics_schema_dto,
                                      data_location=data_location)
        return run_metric_dto

    @classmethod
    def create_metric_dto(cls, name, value,
                          data_location=None,
                          description="",
                          metric_type="vienna.custom"):
        """create a new run_metric Dto"""
        # Load cells and handle list vs non list cells
        num_cells, cells = (len(value), value) if isinstance(value, list) else (1, [value])
        seen = set()
        properties = []
        for cell in cells:
            for key in cell:
                if key not in seen:
                    val = cell[key]
                    properties.append(MetricsClient.get_value_property(name, val, key))
                    seen.add(key)

        metrics_schema_dto = MetricSchemaDto(num_properties=len(properties),
                                             properties=properties)
        metric_dto = MetricDto(metric_id=get_new_id(),
                               metric_type=metric_type,
                               created_utc=get_timestamp(),
                               name=name,
                               description=description,
                               num_cells=num_cells,
                               cells=cells,
                               schema=metrics_schema_dto,
                               data_location=data_location)
        return metric_dto

    def flush(self, timeout_seconds=120):
        with self._log_context("FlushingMetricsClient"):
            self._task_queue.flush(self.identity, timeout_seconds=timeout_seconds)

    def _log(self, *args, **kwargs):
        metric_dto = MetricsClient.create_metric_dto(*args, **kwargs)
        if isinstance(self._task_queue, BatchTaskQueue):
            self._task_queue.add_item(metric_dto)
        else:
            if self.api_route == MetricsClient.OLD_ROUTE:
                func = self._client.legacy_runmetric.post
            else:
                func = self._client.run_metric.post

            ident = "{}_{}".format(self._task_queue._tasks.qsize(), self._task_queue._identity)
            async_task = self._execute_with_run_arguments(func,
                                                          metric_dto,
                                                          is_async=True,
                                                          new_ident=ident)
            self._task_queue.add_task(async_task)
            return async_task

    def _log_batch(self, metric_dtos, is_async=False):
        if len(metric_dtos) > AZUREML_MAX_NUMBER_METRICS_BATCH:
            raise AzureMLException("Number of metrics {} is greater than "
                                   "the max number of metrics that should be "
                                   "sent in batch {}".format(len(metric_dtos),
                                                             AZUREML_MAX_NUMBER_METRICS_BATCH))

        batch_metric_dto = BatchMetricDto(metric_dtos)
        func = self._client.run_metric.post_batch
        res = self._execute_with_run_arguments(func,
                                               batch_metric_dto,
                                               is_async=is_async)
        return res

    def log_scalar(self, name, value, description=""):
        """log scalar type metric"""
        cell = MetricsClient.to_cells([name], [value])
        return self._log(name, cell,
                         description=description,
                         metric_type=AZUREML_SCALAR_METRIC_TYPE)

    def _log_image(self, name, value, **kwargs):
        cell = MetricsClient.to_cells([name], [value])
        return self._log(name, cell,
                         metric_type=AZUREML_IMAGE_METRIC_TYPE, **kwargs)

    def log_list(self, name, values, description=""):
        """log list type metric"""
        value_list = [val for val in values]
        self._check_is_valid_list(value_list)
        cells = MetricsClient.to_cells((name for i in range(len(value_list))), value_list)
        return self._log(name, cells,
                         description=description,
                         metric_type=AZUREML_LIST_METRIC_TYPE)

    def log_row(self, name, value, description=""):
        """log a row as table metric"""
        self._check_is_valid_table(value, is_row=True)
        cells = MetricsClient.to_cells(value.keys(), value.values())
        return self._log(name, cells,
                         description=description,
                         metric_type=AZUREML_TABLE_METRIC_TYPE)

    def log_table(self, name, value, description=""):
        """log a table metric"""
        self._check_is_valid_table(value)
        names = (key for key in value for i in range(len(value[key])))
        values = (value[key][i] for key in value for i in range(len(value[key])))
        cells = MetricsClient.to_cells(names, values)

        return self._log(name,
                         cells,
                         description=description,
                         metric_type=AZUREML_TABLE_METRIC_TYPE)

    def log_confusion_matrix(self, name, data_location=None, description=""):
        """log a JSON string"""
        cell = MetricsClient.to_cells([name], [None])
        return self._log(name, cell,
                         data_location=data_location,
                         description=description,
                         metric_type=AZUREML_CONFUSION_MATRIX_METRIC_TYPE)

    def log_accuracy_table(self, name, data_location=None, description=""):
        """log a JSON string"""
        cell = MetricsClient.to_cells([name], [None])
        return self._log(name, cell,
                         data_location=data_location,
                         description=description,
                         metric_type=AZUREML_ACCURACY_TABLE_METRIC_TYPE)

    def log_residuals(self, name, data_location=None, description=""):
        """log a JSON string"""
        cell = MetricsClient.to_cells([name], [None])
        return self._log(name, cell,
                         data_location=data_location,
                         description=description,
                         metric_type=AZUREML_RESIDUALS_METRIC_TYPE)

    def log_predictions(self, name, data_location=None, description=""):
        """log a JSON string"""
        cell = MetricsClient.to_cells([name], [None])
        return self._log(name, cell,
                         data_location=data_location,
                         description=description,
                         metric_type=AZUREML_PREDICTIONS_METRIC_TYPE)

    def __enter__(self):
        self._logger.debug(START_MSG)
        return self

    def __exit__(self, *args):
        self.flush()
        self._logger.debug(STOP_MSG)

    def _is_valid_scalar(self, value):
        value_type = type(value)
        for number_type in six.integer_types + (float,):
            if isinstance(value, number_type) and sys.getsizeof(value) > AZUREML_MAX_NUMBER_SIZE_IN_BITS:
                raise AzureMLException("Number size of {} is larger than "
                                       "the max size of {} bits".format(value_type,
                                                                        AZUREML_MAX_NUMBER_SIZE_IN_BITS))

        return any(value_type in dictionary
                   for dictionary in (MetricsClient._type_to_metric_type, MetricsClient._type_to_converter))

    def _check_is_valid_scalar(self, value):
        if not self._is_valid_scalar(value):
            valid_types = list(MetricsClient._type_to_metric_type.keys())
            raise AzureMLException("Value of type {0} is not supported, "
                                   "supported types include {1}".format(type(value),
                                                                        valid_types))

    def _check_is_valid_list(self, list_value):
        if isinstance(list_value, list):
            index_of_reference = 0
            reference_type = type(list_value[index_of_reference]) if len(list_value) > 0 else None
            for i in range(len(list_value)):
                val = list_value[i]
                if not self._is_valid_scalar(val):
                    valid_types = list(MetricsClient._type_to_metric_type.keys())
                    raise AzureMLException("Value of type {0} is not supported, "
                                           "supported types include {1}".format(type(list_value),
                                                                                valid_types))
                elif type(val) != reference_type:
                    raise AzureMLException("Scalars at index {0} and {1} differ "
                                           "in type. type: {2} != {3}.".format(i,
                                                                               index_of_reference,
                                                                               type(val),
                                                                               reference_type))

    def _get_length(self, value):
        return len(value) if isinstance(value, list) else 1

    def _check_is_valid_table(self, table, is_row=False):
        if not isinstance(table, dict):
            raise AzureMLException("Table to log is not a dictionary, currently"
                                   "supported inputs are dict[string]: column\n"
                                   " where columns are scalars or a list of scalars")
        if is_row:
            for key in table:
                val = table[key]
                if isinstance(val, list):
                    raise AzureMLException("Row metrics cannot contain list values, "
                                           "column {0} contains a list value".format(key))
                else:
                    self._check_is_valid_scalar(val)

        keys = list(table.keys())
        if len(keys) > 0:
            reference_column = keys[0]
            table_column_length = self._get_length(table[reference_column])
            for key in table:
                column_length = self._get_length(table[key])
                if column_length != table_column_length:
                    raise AzureMLException("Columns must have the same length, "
                                           "column {0} had length {1}, "
                                           "however, column {2} had length {3}.".format(reference_column,
                                                                                        table_column_length,
                                                                                        key,
                                                                                        column_length))
        return table

    @staticmethod
    def get_value_property(name, value, property_id=None):
        """get metrics value property"""
        property_id = property_id if property_id else name
        prop = MetricSchemaPropertyDto(property_id=property_id,
                                       name=name,
                                       type=MetricsClient.get_azureml_type(value))
        return prop

    @staticmethod
    def get_azureml_type(value):
        """get metrics type"""
        return MetricsClient._type_to_metric_type.get(type(value), "string")
