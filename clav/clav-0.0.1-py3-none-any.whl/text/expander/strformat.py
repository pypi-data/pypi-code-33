from clav.os import dump
from clav.text.expander.base import Expander

class StrFormat(Expander):
  'Expand templates using str.format().'

  def __init__(self):
    super().__init__()

  def expands(self, env, tmpl):
    '''
    Expand a template.

    :param dict env: expansion environment
    :param str tmpl: template text
    :returns: The expanded template.
    :rtype: str
    '''
    return tmpl.format(**env)

  def expandf(self, env, tmpl, dst):
    '''
    Expand a template to a file. File will be written only when the expanded
    template differs from the existing file's contents, if any.

    :param str env: expansion environment
    :param str tmpl: template text
    :param str dst: destination file path
    :returns: True if dst file was written
    :rtype bool:
    '''
    return dump(dst, tmpl.format(**env))

strformat = StrFormat()
