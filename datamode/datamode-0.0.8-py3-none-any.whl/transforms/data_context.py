import os, abc

from .core.transform_core import TransformResult

from .load import get_engine_and_conn, get_s3_client
from ..utils import dbutils, validator
from ..utils.yamlutils import load_yaml

from datamode.utils.utils import get_logger
log = get_logger(__name__)


class DataContext(abc.ABC):
  def __init__(self, options, *args, **kwargs):
    self.options = options
    self.result = TransformResult()

  def sync_tcon_with_options(self, tcon):
    # Defaults if we don't have anything specified
    passed_conn_name = self.options.get('conn', None)
    passed_conn_config = self.options.get('conn_config', {})

    if passed_conn_name:
      conn_config = tcon.get_conn_config(conn_name=passed_conn_name, default_return={})
      if passed_conn_config:
        conn_config.update(passed_conn_config)
      elif not passed_conn_config and not conn_config:
        raise Exception(f'Configuration details for `{passed_conn_name}` could not be found.')
    else:
      passed_conn_name = '__temp__'
      conn_config = passed_conn_config

    tcon.integrate_conn_config(passed_conn_name, conn_config)
    tcon.set_conn_meta('current_conn', passed_conn_name)

  def discover_data_type(self, tcon):
    """
    Different data types have different methods of
    sourcing/sinking data. This function discovers type.
      - if a 'path' paramter was passed then data type is a file
      - if a 'df' parameter was passed then data type is a dataframe
      - else it assumes a SQL/remote connection with config from
        the YAML or passed in using conn/conn_config.
    """
    if self.options.get('path', None):
      validator.validate_file_options(self.options)
      if self.options.get('file_type', None):
        data_type = self.options['file_type']
      else:
        _, data_type = os.path.splitext(self.options['path'])
      if data_type:
        data_type = data_type.replace('.','')
      else:
        raise Exception(f'`file_type` must be passed or `path` must include a filename with an extension (e.g. - myfile.csv).')

    elif self.options.get('df', None) is not None:
      validator.validate_df_options(self.options)
      data_type = 'df'

    else:
      validator.validate_sql_options(self.options)
      if self.options.get('conn_config', {}) or self.options.get('conn', None):
        self.sync_tcon_with_options(tcon)
        conn_name = tcon.get_conn_meta('current_conn')
      else:
        # try to use default and set as current context
        conn_name = tcon.get_conn_meta('default_conn')
        if not conn_name:
          raise Exception('No connection configurations have been passed and a default has not been set.')
        tcon.set_conn_meta('current_conn', conn_name)

      conn_config = tcon.get_conn_config(conn_name)
      data_type = conn_config['type']

    return data_type

  def build_sql_conn(self, conn_config):
    con_str = dbutils.sql_con_str(conn_config)
    eng, conn = get_engine_and_conn(con_str)

    return eng, conn

  def ensure_sql_conn(self, tcon):
    current_conn_name = tcon.get_conn_meta('current_conn')
    current_conn_context = tcon.get_conn_config(current_conn_name)

    if not current_conn_context.get('__conn', None):
      current_conn_context = tcon.get_conn_config(conn_name=current_conn_name)
      if not current_conn_context:
        raise Exception(f'Database configuration details could not be found for `{current_conn_name}`')

      current_conn_context['__engine'], current_conn_context['__conn'] = self.build_sql_conn(current_conn_context)
      tcon.integrate_conn_config(current_conn_name, current_conn_context)

  def ensure_s3_conn(self, tcon):
    current_conn_name = tcon.get_conn_meta('current_conn')
    current_conn_context = tcon.get_conn_config(current_conn_name)

    if not current_conn_context.get('__conn', None):
      current_conn_context = tcon.get_conn_config(conn_name=current_conn_name)
      if not current_conn_context:
        raise Exception(f'Database configuration details could not be found for `{current_conn_name}`')

      current_conn_context['__conn'] = get_s3_client(current_conn_context)
      current_conn_context['__engine'] = None

      tcon.integrate_conn_config(current_conn_name, current_conn_context)