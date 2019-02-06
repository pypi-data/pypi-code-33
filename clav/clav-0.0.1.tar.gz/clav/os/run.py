'''
Run command-line programs.

Provides:

- ``run(argv, mode=, env=, cwd=)`` run command-line programs
- ``run.result`` class of the return value of ``run()``
- ``run.error`` class of the exception raised by ``run()``
- ``run.quash`` context manager to supress raising of errors on non-zero exit
- ``run.hook`` context manager to call run with stdout/stderr read hooks
- ``run.stty`` context manager to call run with a stty configuration
'''

import os
import logging
import shlex
import sys
from io import StringIO
from ptyprocess import PtyProcessUnicode
from subprocess import Popen, PIPE
from clav.thread import rbuffer

def shjoin(argv):
  'Join a list of command-line arguments using ``shlex.quote()``.'

  if isinstance(argv, str):
    raise ValueError("'argv' cannot be a 'str' instance")
  return ' '.join(shlex.quote(a) for a in argv)

class BaseRunResult:
  'Base class for ``RunResult`` and ``RunError`.'

  def __init__(self, *args):
    super().__init__()
    if len(args) == 1 and isinstance(args[0], BaseRunResult):
      for _ in 'argv', 'code', 'stdout', 'stderr':
        setattr(self, _, getattr(args[0], _))
    else:
      self.argv = args[0]
      self.code = args[1]
      self.stdout = args[2]
      self.stderr = args[3]

  def format(self, fmt='yaml'):
    '''
    Format result.

    :param str fmt: key into clav.text.formats, e.g. 'json', 'yaml'
    :returns: the run results, formatted as ``fmt``
    :rtype: str
    '''
    from clav.text import formats
    return formats[fmt].dumps({'run': self.__dict__})

  def print(self, fmt='yaml', fd=None):
    '''
    Print result.

    :param str fmt: key into clav.text.formats, e.g. 'json', 'yaml'
    :param file fd: file object to receive run results formatted as ``fmt``
    '''

    fd = sys.stdout if fd is None else fd
    fd.write(self.format(fmt=fmt))
    if hasattr(fd, 'flush') and callable(fd.flush):
      fd.flush()

class RunResult(BaseRunResult):
  'Describe the exit conditions of a call to ``run()``.'

  def __init__(self, *args):
    super().__init__(*args)

class RunError(RuntimeError, BaseRunResult):
  '''
  Raised to describe the conditions of a call to by ``run()`` on non-zero exit.
  '''

  def __init__(self, *args):
    BaseRunResult.__init__(self, *args)
    msg = f'Process exited with code {self.code}: {self.argv}'
    RuntimeError.__init__(self, msg)

class QuashRunError:
  '''
  A context manager which while entered prevents ``run()`` from raising errors
  on non-zero exits. Supports nesting.

  Example:

  ```
  with run.quash():
    run('/bin/false')
  print('hello')
  ```

  ``/bin/false`` exits with status 1, which would normally cause ``run()`` to
  raise ``run.error``, and 'hello' would not be printed. Since we quash errors
  from ``run()``, 'hello' would be printed.
  '''

  def __enter__(self):
    self.old = run.raise_errors
    run.raise_errors = False
    return None

  def __exit__(self, *exc):
    run.raise_errors = self.old
    if exc != (None, None, None):
      return False

class RunHook:
  '''
  Context manager to register hooks to receive stdout and stderr lines for
  invocations of ``run()``.

  Example usage:

  1. Use ``print()`` as a hook.
  ```
  with run.hook(print, nl=False):
    run('echo hello there')
  ```
  prints
  ```
  hello there
  ```
  2. Use logger objects as hooks.
  ```
  import logging
  logger = logging.getLogger()
  with run.hook(logger.debug, nl=False):
    run('find /tmp -type f')
  ```
  3. Separate stdout and stderr hooks.
  ```
  def echo_stdout(line):
    print(f'FROM STDOUT: {line}')

  def echo_stderr(line):
    print(f'FROM STDERR: {line}')

  with run.hook([(echo_stdout, echo_stderr)], nl=False):
    run('echo hello stdout; echo hello stderr 1>&2', mode='sh')
  ```
  prints
  ```
  FROM STDOUT: hello stdout
  FROM STDERR: hello stderr
  ```
  4. Using file objects as hooks.
  ```
  import sys
  with run.hook([(sys.stdout.write, sys.stderr.write)]):
    run('echo hello stdout; echo hello stderr 1>&2', mode='sh')
  ```
  prints
  ```
  hello stdout # to stdout
  hello stderr # to stderr
  ```
  '''

  def __init__(self, hooks, nl=True, excl=False):
    '''
    :param [callable, list] hooks: stdout/stderr hooks
    :param bool nl: if True, newlines are removed before being passed to hook
    :param book excl: if True, disable existing handlers for this context

    Each hook will be passed a line of text as read from stdout or stderr
    while the process runs.

    ``hooks`` may be:

    - a callable: the argument will be called with output from both stdout and
      stderr.
    - a list of callables and/or pairs of callables:
      - a callable will receive output from both stdout and stderr.
      - for a pair of callables, the first callable will receive stdout, and
         the second stderr. One of the two may be None, but both may not be
         None.

    If ``nl`` is ``True`` (the default), then trailing newlines are included in
    the line passed to each hook; or if ``False``, trailing newlines are removed
    from each line before being passed to each hook.

    If ``excl`` (exclusive) is True, any existing handlers will be removed
    for the duration of this context, useful when nesting contexts.
    '''
    super().__init__()
    self.hooks = hooks
    self.nl = nl
    self.excl = excl

  def _is_list(self, o):
    'True if o implements the list methods we require.'

    list_attrs = ('__getitem__', '__len__', '__iter__')
    return all(hasattr(o, _) for _ in list_attrs)

  def _is_pair(self, o):
    'True if o is a pair of stdout/stderr handlers.'

    return (
      self._is_list(o) and
      len(o) == 2 and
      all(callable(_) or _ is None for _ in o) and
      not all(_ is None for _ in o)
    )

  def _wrap_hook(self, hook):
    'When self.nl is False, wrap hook in function that removes newlines.'

    if self.nl is False:
      def newline_hook(_):
        hook(_.rstrip('\r\n'))
      return newline_hook
    else:
      return hook

  def __enter__(self):
    'Register run hooks.'

    # save current hooks
    self.old_stdout = list(run.hooks_stdout)
    self.old_stderr = list(run.hooks_stderr)
    # clear current hooks if exclusive
    if self.excl:
      run.hooks_stdout.clear()
      run.hooks_stderr.clear()
    # pack single argument into a list
    if callable(self.hooks):
      self.hooks = [self.hooks]
    for _ in self.hooks:
      # a single callable, receives both stdout and stderr
      if callable(_):
        _ = self._wrap_hook(_)
        run.hooks_stdout.append(_)
        run.hooks_stderr.append(_)
      # a pair of (stdout, stderr) hooks
      elif self._is_pair(_):
        stdout, stderr = _
        if stdout:
          run.hooks_stdout.append(self._wrap_hook(stdout))
        if stderr:
          run.hooks_stderr.append(self._wrap_hook(stderr))
      else:
        raise ValueError(f'Invalid hooks: {_} ({type(_)})')

  def __exit__(self, *exc):
    'Unregister run hooks.'

    # restore previous hooks state
    run.hooks_stdout.clear()
    run.hooks_stdout.extend(self.old_stdout)
    run.hooks_stderr.clear()
    run.hooks_stderr.extend(self.old_stderr)

class Stty:

  def __init__(self, spec):
    super().__init__()
    self.spec = spec
    self.log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

  def __enter__(self):
    self.old_tty = None
    try:
      self.old_tty = run('stty -g', env=os.environ).stdout.strip()
    except run.error as ex:
      self.log.debug(f'Failed getting tty:\n{ex.format()}', exc_info=True)
      return
    try:
      run(f'stty {self.spec}', env=os.environ)
    except run.error as ex:
      self.log.debug(f'Failed changing tty:\n{ex.format()}', exc_info=True)

  def __exit__(self, *exc):
    if not self.old_tty:
      return
    try:
      run(f'stty {self.old_tty}', env=os.environ)
    except run.error:
      self.log.debug(f'Failed restoring tty:\n{ex.format()}', exc_info=True)

def runpopen(argv, env=None, cwd=None, shell=False):
  '''
  Run a command using ``Popen``.

  :param [str, list] argv: command to invoke
  :param dict env: environment variables or ``None``
  :param str cwd: working directory for command
  :param bool shell: invoke using the system shell
  :returns: a run result object
  :rtype: run.result
  '''
  p = Popen(
    argv, env=env, shell=shell, cwd=cwd, stdout=PIPE, stderr=PIPE,
    universal_newlines=True,
  )
  def make_hook(hooks):
    if not hooks:
      return None
    def read_hook(_):
      for hook in hooks:
        hook(_)
    return read_hook
  readers = (
    rbuffer(p.stdout.readline, read_hook=make_hook(run.hooks_stdout)),
    rbuffer(p.stderr.readline, read_hook=make_hook(run.hooks_stderr)),
  )
  for r in readers:
    r.join()
  return run.result(argv, p.wait(), *(r.result or '' for r in readers))

def runpty(argv, env=None, cwd=None):
  '''
  Run a command using ``ptyprocess``.

  :param [str, list] argv: command to invoke
  :param dict env: environment variables or ``None``
  :param str cwd: working directory for command
  :returns: a run result object
  :rtype: run.result
  '''
  p = PtyProcessUnicode.spawn(argv, env=env, cwd=cwd)
  buf = StringIO()
  try:
    while True:
      _ = p.readline()
      buf.write(_)
      for hook in run.hooks_stdout:
        hook(_)
  except EOFError:
    pass
  return run.result(argv, p.wait(), buf.getvalue() or '', '')

def run(argv, mode='popen', env=None, cwd=None):
  '''
  Run a command using a popen, the shell, or a pty.

  :param [str, list] argv: command to run
  :param str mode: 'popen', 'sh', or 'pty'
  :param dict env: environment variables or ``None``
  :param str cwd: working directory for command
  :returns: a run result object
  :rtype: run.result
  :raises run.error: on non-zero exit unless quashed

  ``argv`` may be a string (to be parsed by shlex) or a list.

  If ``mode`` is ``'popen'`` (the default), then shell syntax may not be used
  in the command.

  If ``mode`` is ``'sh'``, then the command will be invoked using the system
  shell, and shell syntax may be used in the command.

  If ``mode`` is ``'pty'``, then shell syntax may not be used in the command,
  and the command will be attached to a pseudo-terminal. Programs typically run
  in interactive mode when a pty is detected. A pty has only one output - the
  'screen', in the abstract sense - rather than stdout and stderr.

  ``env`` should be `None`, or a `dict` of environment variables to set for the
  invocation.

  ``cwd`` should be ``None`` or the directory in which to run the command.

  When called outside of the ``run.quash()`` context manager, a ``run.result``
  object is returned if the command exits zero, else a ``run.error`` exception
  is raised if the command exits non-zero.

  When called inside of the ``run.quash()`` context manage, a ``run.result``
  object is returned regardless of the command's exit code.

  When called with ``mode = 'pty'``, the ``stderr`` attribute of the
  ``run.result`` or ``run.error`` will always be an empty string.
  '''
  if mode == 'popen':
    if isinstance(argv, str):
      argv = shlex.split(argv)
    r = runpopen(argv, env=env, cwd=cwd, shell=False)
  elif mode in ('sh', 'shell'):
    if not isinstance(argv, str):
      argv = shjoin(argv)
    r = runpopen(argv, env=env, cwd=cwd, shell=True)
  elif mode == 'pty':
    if isinstance(argv, str):
      argv = shlex.split(argv)
    r = runpty(argv, env=env, cwd=cwd)
  else:
    raise ValueError("'mode' must be 'popen', 'sh', or 'pty'")
  if r.code != 0 and run.raise_errors:
    raise run.error(r)
  return r

run.result = RunResult
'Standard result class returned by ``run()``.'

run.error = RunError
'Standard error raised by ``run()``.'

run.raise_errors = True
'''
If ``True``, then ``run()` will raise ``run.error`` when the command exits with
non-zero status. This is the default, and should only be changed by
``run.quash()``.
'''

run.quash = QuashRunError
'Context manager to suppress raising of ``run.error`` on non-zero exit.'

run.stty = Stty
'Context manager to run commands with a stty configuration.'

run.hook = RunHook
'Context manager to call run with read hooks for stdout/stderr.'

run.hooks_stdout = []
'Active stdout hooks for ``run()``.'

run.hooks_stderr = []
'Active stderr hooks for ``run()``.'
