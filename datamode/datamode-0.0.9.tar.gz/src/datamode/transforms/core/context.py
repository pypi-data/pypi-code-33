from .dataset import Dataset
from .transform_state import TransformState


class TransformContext():
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.conn_context = {
        '_meta': {
          'cnt': 0,
          'current_conn': None,
          'default_conn': None,
        },
        '_context': {},
      }
    self.yaml_config = {}
    self.protected_sinks = []
    self.ds = Dataset()  # Working dataset
    self.current_table = ''

  def add_result(self, transform, result, elapsed):
    table = result.table if result.table else self.current_table

    # Copy the latest tstate into the new one.
    tstate = TransformState(transform, result, self.ds.tstate_last, elapsed)  # tstate_last can be None
    tstate.set_df(table, result.df)

    self.ds.add_tstate(tstate)

  def summary(self):
    summary = '------------------------ Output ----------------------------\n\n '
    return summary + self.ds.summary()

  # Can be None
  @property
  def df_current(self):
    tstate = self.ds.tstate_last

    if not tstate or not self.current_table:
      return None

    return tstate.get_df(self.current_table)

  @property
  def transforms(self):
    return [tstate.transform for tstate in self.ds.tstates]

  def get_conn_meta(self, key=None):
    if key:
      return self.conn_context['_meta'][key]
    else:
      return self.conn_context.get('_meta', {})

  def set_conn_meta(self, key, data):
    self.conn_context['_meta'][key] = data

  def get_conn_config(self, conn_name, default_return=None):
    return self.conn_context.get('_context', {}).get(conn_name, default_return)

  def integrate_conn_config(self, conn_name, conn_config={}):
    if not conn_config.get('type', None):
      raise Exception(f'The connection named {conn_name} must specify `type` but received {conn_config}.')
    # if config with same name exists - replace it entirely
    self.conn_context['_context'].update({conn_name: conn_config})
    self.conn_context['_meta']['cnt'] = len(self.conn_context['_context'].keys())

  def close_conns(self):
    for conn, conn_config in self.conn_context['_context'].items():
      if conn_config.get('__conn', None):
        try:
          conn_config['__conn'].close()
          conn_config['__engine'].dispose()
        except:
          pass

  def __str__(self):
    return f'current_table={self.current_table}, ds={self.ds}'

  def __repr__(self):
    return f'<{type(self).__name__}: {str(self)}>'
