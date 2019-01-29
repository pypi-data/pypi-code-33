import boto3
import pandas as pd
from sqlalchemy import create_engine

from ..utils.utils import log_exception_with_context
from ..utils.data import downsample_dataframe

from datamode.utils.utils import get_logger
log = get_logger(__name__)


def get_engine_and_conn(con_str):
  log.debug(f'Using {con_str} as the connection string')
  engine = create_engine(con_str)
  conn = engine.connect()
  return engine, conn

def get_s3_client(conn_config):
  client = boto3.client('s3',
    aws_access_key_id=conn_config['access_key_id'],
    aws_secret_access_key=conn_config['secret_access_key']
  )
  return client


def get_dataframe_from_sql(conn, table_name):
  df = None
  try:
    df = pd.read_sql(table_name, conn)
  except ValueError as e:
    log_exception_with_context(log, e, f'Error in table {table_name}')

  return df


def get_dataframe_from_csv(path, sample_ratio=None, sample_seed=42):
  df = None
  try:
    # This defaults to using the C engine, which is 3 times faster than the Python engine.
    # It defaults to 'c' though.
    df = pd.read_csv(path)

    if sample_ratio:
      # Todo: make this sample a true ratio instead of a probabilistic attempt at the ratio.
      # Also, make this available for all Source transforms.
      # Pandas has a helper function but for larger datasets, we should use the source engine to downsample (e.g. sql.)
      df = downsample_dataframe(df, sample_ratio, sample_seed)

  except Exception as e:
    log_exception_with_context(log, e, f'Error loading CSV {path}')

  return df


def get_dataframe_from_json(path, sample_ratio=None, sample_seed=42):
  df = None
  try:
    df = pd.read_json(path, orient='records', lines=True)
    if sample_ratio:
      df = downsample_dataframe(df, sample_ratio, sample_seed)
  except Exception as e:
    log_exception_with_context(log, e, f'Error loading CSV {path}')

  return df

