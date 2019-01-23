#TODO: Find a way to substitute default config values when they are needed from within functions
# e.g.: for func_config not in current_config: current_config.func_config = DefaultValue

class BQTOBQConfig:
    def __init__(self):
        # TODO: Find default values for these attributes
        self._full_table = True
        self._query = False
        self._query_file_name = None
        self._write_disposition = 'WRITE_APPEND'
        self._force_dataset_creation = True
        self._force_table_creation = True
        self._use_legacy_sql = False
        self._async_query = False
        self._query_params = {}

    @property
    def query_file_name(self):
        return self._query_file_name

    @query_file_name.setter
    def query_file_name(self, value):
        if not isinstance(value, str):
            raise TypeError('query_file_name must be set to a String Value')
        self._query_file_name = value

    @property
    def query_params(self):
        return self._query_params

    @query_params.setter
    def query_params(self, value):
        if not isinstance(value, dict):
            raise TypeError('query_params must be set to a Dictionary')
        self._query_params = value

    @property
    def async_query(self):
        return self._async_query

    @async_query.setter
    def async_query(self, value):
        if not isinstance(value, bool):
            raise TypeError('async_query must be set to a Boolean Value')
        self._async_query = value

    @property
    def full_table(self):
        return self._full_table

    @full_table.setter
    def full_table(self, value):
        if not isinstance(value, bool):
            raise TypeError('Print Header must be set to a Boolean Value (True/False')
        self._full_table = value

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        if not isinstance(value, str):
            raise TypeError('Query must be set to a Str Value')
        self._query = value

    @property
    def write_disposition(self):
        return self._write_disposition

    @write_disposition.setter
    def write_disposition(self, value):
        if value not in ['WRITE_APPEND', 'WRITE_EMPTY', 'WRITE_TRUNCATE']:
            raise TypeError("write_disposition must be one of: 'WRITE_APPEND', 'WRITE_EMPTY', 'WRITE_TRUNCATE'")
        self._write_disposition = value

    @property
    def force_table_creation(self):
        return self._force_table_creation

    @force_table_creation.setter
    def force_table_creation(self, value):
        if not isinstance(value, str):
            raise TypeError('force_table_creation must be set to a String Value')
        self._force_table_creation = value
    @property
    def force_dataset_creation(self):
        return self._force_dataset_creation

    @force_dataset_creation.setter
    def force_dataset_creation(self, value):
        if not isinstance(value, str):
            raise TypeError('force_dataset_creation must be set to a String Value')
        self._force_dataset_creation = value

    @property
    def use_legacy_sql(self):
        return self._use_legacy_sql

    @use_legacy_sql.setter
    def use_legacy_sql(self, value):
        if not isinstance(value, str):
            raise TypeError('use_legacy_sql must be set to a Boolean Value')
        self._use_legacy_sql = value


class BQTOCSVConfig:
    def __init__(self):
        # TODO: Find default values for these attributes
        self._field_delimiter = '§'
        # TODO: discuss whether we need a quote character for String fields
        self._quote_character = ''
        self._use_legacy_sql = False
        self._print_header = False
        self._full_table = True
        self._query = False
        self._storage_retention = False
        self._gs_bucket = None
        self._gs_filename = None

    @property
    def use_legacy_sql(self):
        return self._use_legacy_sql

    @use_legacy_sql.setter
    def use_legacy_sql(self, value):
        if not isinstance(value, bool):
            raise TypeError('use_legacy_sql must be set to a String Value')
        self._use_legacy_sql = value

    @property
    def print_header(self):
        return self._print_header

    @print_header.setter
    def print_header(self, value):
        if not isinstance(value, bool):
            raise TypeError('Print Header must be set to a Boolean Value (True/False')
        self._print_header = value

    @property
    def full_table(self):
        return self._full_table

    @full_table.setter
    def full_table(self, value):
        if not isinstance(value, bool):
            raise TypeError('full_table must be set to a Boolean Value (True/False')
        self._full_table = value

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        if not isinstance(value, str):
            raise TypeError('Query must be set to a Str Value')
        self._query = value

    @property
    def field_delimiter(self):
        return self._query

    @field_delimiter.setter
    def field_delimiter(self, value):
        if not isinstance(value, str):
            raise TypeError('Query must be set to a Str Value')
        self._field_delimiter = value

    @property
    def storage_retention(self):
        return self._storage_retention

    @storage_retention.setter
    def storage_retention(self, value):
        if not isinstance(value, bool):
            raise TypeError('source_format must be set to a Boolean Value')
        self._storage_retention = value

    @property
    def gs_bucket(self):
        return self._gs_bucket

    @gs_bucket.setter
    def gs_bucket(self, value):
        if not isinstance(value, str):
            raise TypeError('source_format must be set to a String Value')
        self._gs_bucket = value

    @property
    def gs_filename(self):
        return self._gs_filename

    @gs_filename.setter
    def gs_filename(self, value):
        if not isinstance(value, str):
            raise TypeError('source_format must be set to a String Value')
        self._gs_filename = value


class BQTOMySQLConfig:
    # TODO: Discuss, can we just ignore all the CSV intermediate steps and then just set up the most robust default way to go from SOURCE > CSV > TARGET
    def __init__(self):
        # TODO: Find default values for these attributes
        self._write_disposition = 'WRITE_EMPTY'

    @property
    def write_disposition(self):
        return self._write_disposition

    @write_disposition.setter
    def write_disposition(self, value):
        if not isinstance(value, str):
            raise TypeError('source_format must be set to a String Value')
        self._write_disposition = value


class CSVTOBQConfig:
    def __init__(self):
        # TODO: Find default values for these attributes
        self._create_disposition = 'CREATE_IF_NEEDED'
        self._write_disposition = 'WRITE_EMPTY'
        self._field_delimiter = '§'
        self._print_header = False # Needed???
        self._source_format = 'CSV'
        self._allow_quoted_newlines = False
        self._quote_character = None
        self._skip_leading_rows = None
        self._ignore_unknown_values = None
        self._max_bad_records = 0
        self._allow_jagged_rows = None
        self._partitioned_field = None
        self._expiry = None
        self._auto_generate_schema = False

    @property
    def create_disposition(self):
        return self._create_disposition

    @create_disposition.setter
    def create_disposition(self, value):
        if not isinstance(value, str):
            raise TypeError('source_format must be set to a String Value')
        self._create_disposition = value

    @property
    def write_disposition(self):
        return self._write_disposition

    @write_disposition.setter
    def write_disposition(self, value):
        if not isinstance(value, str):
            raise TypeError('source_format must be set to a String Value')
        self._write_disposition = value

    @property
    def source_format(self):
        return self._source_format

    @source_format.setter
    def source_format(self, value):
        if not isinstance(value, str):
            raise TypeError('source_format must be set to a String Value')
        self._source_format = value

    @property
    def field_delimiter(self):
        return self._field_delimiter

    @field_delimiter.setter
    def field_delimiter(self, value):
        """
        :param value: Time in Minutes for when the table should expire (delete itself)
        :return: Nothing
        """
        if not isinstance(value, str):
            raise TypeError('Field Delimiter must be a String')
        elif len(value) != 1:
            raise TypeError('Field Delimiter must be of length 1')

        self._field_delimiter = value

    @property
    def allow_quoted_newlines(self):
        return self._allow_quoted_newlines

    @allow_quoted_newlines.setter
    def allow_quoted_newlines(self, value):
        if not isinstance(value, bool):
            raise TypeError('allow_quoted_newlines must be set to a Boolean Value')
        self._allow_quoted_newlines = value

    @property
    def skip_leading_rows(self):
        return self._skip_leading_rows

    @skip_leading_rows.setter
    def skip_leading_rows(self, value):
        if not isinstance(value, bool):
            raise TypeError('skip_leading_rows must be set to a Boolean Value')
        self._skip_leading_rows = value

    @property
    def max_bad_records(self):
        return self._max_bad_records

    @max_bad_records.setter
    def max_bad_records(self, value):
        if not isinstance(value, int):
            raise TypeError('max_bad_records must be set to a Integer Value')
        self._max_bad_records = value

    @property
    def allow_jagged_rows(self):
        return self._allow_jagged_rows

    @allow_jagged_rows.setter
    def allow_jagged_rows(self, value):
        if not isinstance(value, bool):
            raise TypeError('allow_jagged_rows must be set to a Boolean Value')
        self._allow_jagged_rows = value

    @property
    def quote_character(self):
        return self._quote_character

    @quote_character.setter
    def quote_character(self, value):
        if not isinstance(value, str):
            raise TypeError('quote_character must be set to a String Value')
        self._quote_character = value

    @property
    def ignore_unknown_values(self):
        return self._ignore_unknown_values

    @ignore_unknown_values.setter
    def ignore_unknown_values(self, value):
        if not isinstance(value, bool):
            raise TypeError('ignore_unknown_values must be set to a Boolean Value')
        self._ignore_unknown_values = value

    @property
    def print_header(self):
        return self._print_header

    @print_header.setter
    def print_header(self, value):
        if not isinstance(value, bool):
            raise TypeError('Print Header must be set to a Boolean Value (True/False')
        self._print_header = value

    @property
    def expiry(self):
        return self._expiry

    @expiry.setter
    def expiry(self, value):
        """
        :param value: Time in Minutes for when the table should expire (delete itself)
        :return: Nothing
        """
        if not isinstance(value, int):
            raise TypeError('Partitioned Field must be an Integer')

        self._expiry = value

    @property
    def partitioned_field(self):
        return self._partitioned_field

    @partitioned_field.setter
    def partitioned_field(self, value):
        """
        :param value: Field (String) to set as the field to partition the table on
        :return: Nothing
        """
        if not isinstance(value, str):
            raise TypeError('Partitioned Field must be a String')

        self._partitioned_field = value

    @property
    def auto_generate_schema(self):
        return self._auto_generate_schema

    @auto_generate_schema.setter
    def auto_generate_schema(self, value):
        if not isinstance(value, bool):
            raise TypeError('source_format must be set to a Boolean Value')
        self._auto_generate_schema = value


class CSVTOMySQLConfig:
    #As above
    pass


class MySQLTOBQConfig:
    # TODO: Discuss, can we just ignore all the CSV intermediate steps and then just set up the most robust default way to go from SOURCE > CSV > TARGET
    def __init__(self):
        # TODO: Find default values for these attributes
        self._write_disposition = 'WRITE_EMPTY'
        self._stream = False

    @property
    def write_disposition(self):
        return self._write_disposition

    @write_disposition.setter
    def write_disposition(self, value):
        if not isinstance(value, str):
            raise TypeError('source_format must be set to a String Value')
        self._write_disposition = value

    @property
    def stream(self):
        return self._stream

    @stream.setter
    def stream(self, value):
        if not isinstance(value, str):
            raise TypeError('source_format must be set to a String Value')
        self._stream = value


class BQTableConfig:
    '''
    Could split these configs into the Table and Job configs
    expiry and partition field added to the Table, they are parameters of the table
    and the force creations could go into the jobs
    That would help with the current issue of passing this config alongside the job
    '''
    def __init__(self):
        self.force_table_creation = True
        self.force_dataset_creation = True
        self.dataset_location = 'EU'

    @property
    def force_table_creation(self):
        return self._force_table_creation

    @force_table_creation.setter
    def force_table_creation(self, value):
        if not isinstance(value, bool):
            raise TypeError('force_table_creation must be set to a Boolean Value')
        self._force_table_creation = value

    @property
    def force_dataset_creation(self):
        return self._force_dataset_creation

    @force_dataset_creation.setter
    def force_dataset_creation(self, value):
        if not isinstance(value, bool):
            raise TypeError('force_dataset_creation must be set to a Boolean Value')
        self._force_dataset_creation = value
