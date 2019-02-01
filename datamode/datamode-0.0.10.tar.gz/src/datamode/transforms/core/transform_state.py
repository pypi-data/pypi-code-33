class TransformState():
  def __init__(self, transform=None, result=None, tstate_orig=None, elapsed=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.dfs = {}  # Dict of dataframes
    self.transform = transform
    self.result = result  # Legacy until we can refactor this
    self.source_tables = []
    self.dest_tables = []
    self.working_table = None
    self.elapsed = elapsed

    if tstate_orig:
      self.copy_dataframes_from_other(tstate_orig)

  def set_df(self, name, df):
    self.working_table = name
    self.dfs[name] = df

    # Todo: this will have to be refactored when we actually work with multiple tables.
    self.source_tables.append(name)
    self.dest_tables.append(name)

  def get_working_df(self):
    return self.get_df(self.working_table)

  def get_df(self, name):
    return self.dfs.get(name)

  def has_df(self, name):
    return name in self.dfs

  def copy_dataframes_from_other(self, other_tstate):
    # Intentional shallow copy.
    # We want to keep refs to dataframes but not dupe them unless necessary
    self.dfs = other_tstate.dfs.copy()

  @property
  def table_names(self):
    return self.dfs.keys()

  def summary(self):
    summary = ''
    for name, df in self.dfs.items():
      summary += f'{name}:\n'
      summary += str(df.head()) + '\n\n'

    return summary

  def __str__(self):
    return f'tables ({len(self.dfs)}): '+ ', '.join(self.dfs.keys())

  def __repr__(self):
    return f'<{type(self).__name__}: {str(self)}>'

  def dump(self):
    dump = self.__repr__() + '\n'
    for name, df in self.dfs.items():
      dump += f'{name}:\n'
      dump += str(df.head()) + '\n\n'

    return dump
