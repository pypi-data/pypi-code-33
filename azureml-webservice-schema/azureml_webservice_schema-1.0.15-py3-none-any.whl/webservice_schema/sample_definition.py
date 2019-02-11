# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for managing Webservice Schema SampleDefinition handling."""

from azureml.webservice_schema.data_types import DataTypes


class SampleDefinition:
    """
    Defines a sample webservice schema definition.

    :param input_type: The type for this input
    :type input_type: DataTypes
    :param sample_data: A sample for this input
    :type sample_data: varies
    """

    def __init__(self, input_type, sample_data):
        """
        Initialize a SampleDefinition object.

        :param input_type: The type for this input
        :type input_type: DataTypes
        :param sample_data: A sample for this input
        :type sample_data: varies
        """
        if input_type is DataTypes.NUMPY:
            from azureml.webservice_schema._numpy_util import NumpyUtil
            self.schema = NumpyUtil.extract_schema(sample_data)
        elif input_type is DataTypes.SPARK:
            from azureml.webservice_schema._spark_util import SparkUtil
            self.schema = SparkUtil.extract_schema(sample_data)
        elif input_type is DataTypes.PANDAS:
            from azureml.webservice_schema._pandas_util import PandasUtil
            self.schema = PandasUtil.extract_schema(sample_data)
        elif input_type is DataTypes.STANDARD:
            from azureml.webservice_schema._python_util import PythonUtil
            self.schema = PythonUtil.extract_schema(sample_data)
        else:
            raise ValueError("Invalid sample definition type: {}. This type is not supported. Please use one of the "
                             "values defined in dataTypes.DataTypes".format(self.type))
        self.type = input_type

    def serialize(self):
        """
        Convert this SampleDefinition object into a json dictionary.

        :return: A json dictionary representation of this object
        :rtype: dict
        """
        return {
            "internal": self.get_schema_string(),
            "swagger": self.schema.swagger,
            "type": self.type,
            "version": self.schema.version}

    def get_schema_string(self):
        """
        Retrieve a string representation of this object.

        :return: A string representation of this object
        :rtype: str
        """
        return self.schema.internal.serialize_to_string()
