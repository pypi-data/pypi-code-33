# Wrapper class for multiple dataframes and metadata.
class Dataset():
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # An ordered list of TransformStates, one for each transform step.
    self.tstates = []

  @property
  def tstate_first(self):
    return self.tstates[0] if self.tstates else None

  @property
  def tstate_last(self):
    return self.tstates[-1] if self.tstates else None

  @property
  def tstate_count(self):
    return len(self.tstates)

  def has_df(self, name):
    tstate = self.tstate_last
    return tstate.has_df(name) if tstate else False

  def add_tstate(self, tstate):
    self.tstates.append(tstate)

  # Pass in the transform_id that you want - defaults to the last state.
  def summary(self, transform_id=-1):
    if not self.tstates:
      return 'Empty dataset'

    tstate = self.tstates[transform_id]
    return tstate.summary()

  # The dataset spans all tstates, so we can't show a list of tables.
  # Instead, we can show a list of the transforms used in this stack.
  def __str__(self):
    transforms = [str(tstate.transform.__class__.__name__) for tstate in self.tstates]
    return ', '.join(transforms)

  def __repr__(self):
    return f'<{type(self).__name__}: {str(self)} ({len(self.tstates)})>'

  def debug_summary(self):
    transforms = [f'{index}: {str(tstate.transform)}' for index, tstate in enumerate(self.tstates) ]
    return '\n'.join(transforms)

  def dump(self):
    dump = f'*** {type(self).__name__} - {len(self.tstates)} tstates ***\n'
    dump += self.debug_summary() + '\n'
    for tstate in self.tstates:
      dump += tstate.dump() + '\n'

    return dump
