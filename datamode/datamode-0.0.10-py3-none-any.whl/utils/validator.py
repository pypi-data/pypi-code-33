from . import dbutils


##################
### Exceptions ###
##################
def raise_missing_options(typ, missing_options, required_options):
  raise TypeError(f'Missing required argument(s) {missing_options}. Operations on `{typ}` types require these options {required_options}.')

def raise_invalid_options(typ, invalid_options, valid_options):
  raise TypeError(f'Received unexpected argument(s) {invalid_options}. Operations on `{typ}` types accept these options {valid_options}.')

def raise_invalid_yaml_structure(options):
  raise Exception(f'The YAML structure is missing these fields {options}.')

def raise_missing_options_in_yaml(name, missing_fields):
  raise Exception(f'The connection {name} is missing one of these required fields {missing_fields}')


##################
### Common Fnc ###
##################
def __one_way_diff(array1, array2):
  """
  Compares two arrays and returns
  items in array1 that do not appear
  in array2. To get diffs going both
  ways use symmetric_difference
  """
  diff = set(array1) - set(array2)

  return list(diff)

def __validate_options(typ, options, required, valid):
  missing_opt = __one_way_diff(required, options)
  if missing_opt:
    raise_missing_options(typ, missing_opt, required)

  extra_opt = __one_way_diff(options, valid)
  if extra_opt:
    raise_invalid_options(typ, extra_opt, valid)


##################
### Validators ###
##################

## Source/Sinks ##
def validate_file_options(options):
  REQUIRED_OPTIONS = ['path']
  VALID_OPTIONS = ['path', 'file_type', 'dfname', 'sample_ratio', 'sample_seed']
  typ = 'file'

  __validate_options(typ, list(options.keys()), REQUIRED_OPTIONS, VALID_OPTIONS)

  return True

def validate_df_options(options):
  REQUIRED_OPTIONS = ['df']
  VALID_OPTIONS = ['df', 'dfname', 'sample_ratio', 'sample_seed']
  typ = 'dataframe'

  __validate_options(typ, list(options.keys()), REQUIRED_OPTIONS, VALID_OPTIONS)

  return True

def validate_sql_options(options):
  REQUIRED_OPTIONS = []
  VALID_OPTIONS = ['conn', 'conn_config', 'query', 'queryfile', 'table', 'dfname',
    'if_exists', 'sample_ratio', 'sample_seed', 'file_type', 'bucket', 'file_key'
  ]
  typ = 'sql'

  __validate_options(typ, list(options.keys()), REQUIRED_OPTIONS, VALID_OPTIONS)

## Loading YAML ##
def validate_yaml_data_connections(options):
  REQUIRED_OPTIONS = ['type', 'host']
  REQUIRED_S3_OPTIONS = ['type', 'access_key_id', 'secret_access_key']
  VALID_OPTIONS = ['type', 'host', 'port', 'user', 'password', 'dbname', 'schema',
    'access_key_id', 'secret_access_key'
  ]
  EXTRA_OPTIONS = []

  if options.get('connections', None):
    for conn_name, conn_config in options['connections'].items():
      if conn_config.get('type', 'None').upper() in dbutils.ALL_S3_TYPES:
        if all(opt in conn_config for opt in REQUIRED_S3_OPTIONS):
          pass
        else:
          raise_missing_options_in_yaml(conn_name, REQUIRED_S3_OPTIONS)
      else:
        if all(opt in conn_config for opt in REQUIRED_OPTIONS):
          pass
        else:
          raise_missing_options_in_yaml(conn_name, REQUIRED_OPTIONS)
  else:
    raise_invalid_yaml_structure(['connections'])

  return True