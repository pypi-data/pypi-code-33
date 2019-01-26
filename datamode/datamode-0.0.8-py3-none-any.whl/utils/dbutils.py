POSTGRES_TYPES = ['POSTGRES', 'PSQL', 'POSTGRESQL']
MYSQL_TYPES = ['MYSQL']
SQLITE_TYPES = ['SQLITE']
ALL_SQL_TYPES = POSTGRES_TYPES + MYSQL_TYPES + SQLITE_TYPES

ALL_S3_TYPES = ['S3']

CSV_TYPES = ['CSV']
JSON_TYPES = ['JL', 'JSONL', 'JSONLINES', 'JSON']
ALL_FILE_TYPES = CSV_TYPES + JSON_TYPES

ALL_DATAFRAME_TYPES = ['DF', 'DATAFRAME']

# should eventually add s3,
def build_postgres_con_str(config):
  # TODO: Allow different drivers:
  # like none or pg8000

  db_host = 'localhost' if not config.get('host', None) else config.get('host')
  db_port = 5432 if not config.get('port', None) else config.get('port')
  db_user = config['user']
  db_pass = config.get('password', None)
  db_schema = config.get('schema', 'public')
  db_name = config['dbname']
  psql_con_str = f'postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

  return psql_con_str

def build_mysql_con_str(config):

  db_host = 'localhost' if not config.get('host', None) else config.get('host')
  db_port = 3306 if not config.get('port', None) else config.get('port')
  db_user = config['user']
  db_pass = config.get('password', None)
  db_name = config['dbname']
  mysql_con_str = f'mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

  return mysql_con_str

def build_sqlite_con_str(config):

  path_to_db = config['host']
  sqlite_con_str = f'sqlite:///{path_to_db}'

  return sqlite_con_str

def sql_con_str(dbc):
  if dbc['type'].upper() in SQLITE_TYPES:
    con_str = build_sqlite_con_str(dbc)
  elif dbc['type'].upper() in POSTGRES_TYPES:
    con_str = build_postgres_con_str(dbc)
  elif dbc['type'].upper() in MYSQL_TYPES:
    con_str = build_mysql_con_str(dbc)

  return con_str