import threading
from itertools import count

class Thread(threading.Thread):
  '''
  Thin wrapper for ``threading.Thread`` which captures results and errors, and
  provides a ``spawn`` method.
  '''

  @classmethod
  def spawn(cls, *a, **kw):
    t = cls(*a, **kw)
    t.start()
    return t

  _id = count()

  @classmethod
  def _next_id(cls):
    cls._id += 1
    return cls._id

  def __init__(self, target, args=(), kwargs={}, name=None, daemon=True):
    name = name if name else f'clav thread {next(self._id)}'
    self.target = target
    self.args = args
    self.kwargs = kwargs
    self.result = None
    self.error = None
    super().__init__(name=name, target=self._main)
    self.daemon = daemon

  def _main(self):
    try:
      self.result = self.target(*self.args, **self.kwargs)
    except:
      self.error = sys.exc_info()
      raise

class ReadBuffer:
  '''
  Use a thread to buffer data from a blocking file descriptor.

  The constructor accepts a read function ``readf`` and an eof condition
  ``eof``. ``readf`` will be called, and its return values buffered, until
  ``readf`` returns an object that matches the ``eof`` condition. The default
  ``eof`` matches any empty sequence, such as ``''`` or ``b''``.

  ``eof`` may be a callable, to which the result of ``readf`` is passed, or a
  sequence, against which the result of ``readf`` is compared for equality.

  The thread is started via ``start()``. The thread's main loop will break early
  if ``stop()`` is called.

  When the ``eof`` condition is satisfied, or an error occurs, the thread will
  stop running, and ``is_alive()`` will return ``False``.

  If no data was read from ``readf`` before EOF, then both ``get_result()`` and
  ``get_error()`` will return ``None``.

  If data was read from ``readf`` and EOF was encountered without error, then
  ``get_result()`` will return the buffered data as a sequence of the
  appropriate type, and ``get_error()`` will return ``None``.

  If an error ocurred while reading, then ``get_error()`` will return an
  ``exc_info`` tuple, and ``get_result()`` will return any data buffered before
  the error condition occurred, or ``None`` if no data was buffered.

  The type of buffer used depends on the type of data returned by the first
  call to ``readf``, unless the caller explicitly provides a buffer type via the
  ``buftype`` constructor argument.
  '''

  @classmethod
  def spawn(cls, *a, **kw):
    'Create, start, and return a new instance.'

    rb = cls(*a, **kw)
    rb.start()
    return rb

  _id = 0

  @classmethod
  def _next_id(cls):
    cls._id += 1
    return cls._id

  def __init__(self, readf, eof=None, name=None, buftype=None, read_hook=None):
    super().__init__()
    if callable(readf):
      self.readf = readf
    elif not callable(readf) and hasattr(readf, 'read') and callable(readf.read):
      self.readf = readf.read
    else:
      raise ValueError(f'readf is neither callable nor file object: {readf}')
    self.eof = eof if eof else lambda i: len(i) == 0
    self.name = name if name else 'clav rbuffer {self._next_id()}'
    self.buftype = buftype
    self.thread = Thread(target=self.read, name=name)
    self.work = True
    self.read_hook = read_hook
    self._result = None

  def is_eof(self, r):
    'Return `True` if `r` matches the eof condition, else `False`.'

    return self.eof(r) if callable(self.eof) else r == self.eof

  def read(self):
    '''
    Read data from ``self.readf`` to a buffer until EOF, and save the buffer to
    ``self.result``.
    '''

    buf = None
    try:
      r = self.readf()
      if self.is_eof(r):
        return
      if self.buftype:
        buf = self.buftype()
      else:
        buf = BytesIO() if hasattr(r, 'decode') else StringIO()
      buf.write(r)
      if self.read_hook:
        self.read_hook(r)
      while self.work:
        r = self.readf()
        if self.is_eof(r):
          break
        buf.write(r)
        if self.read_hook:
          self.read_hook(r)
    finally:
      if buf:
        self._result = buf.getvalue()

  def start(self):
    'Start buffering data from ``self.readf`` in a thread.'

    self.thread.start()

  def stop(self):
    '''
    Stop buffering data from ``self.readf``` in a thread.

    This will not necessarily stop the thread immediately, as it could be
    blocking in a read, but rather will break the thread's main loop once its
    current iteration is complete. Call ``join()`` to wait on the thread after
    calling this method.
    '''

    self.work = False

  def is_alive(self):
    'Return ``True`` if the thread is buffering, else ``False``.'

    return self.thread.is_alive()

  def join(self, timeout=None):
    '''
    Wait for the thread to stop with optional floating-point ``timeout`` in
    seconds. When using ``timeout``, call ``is_alive()`` to see whether the
    thread has stopped.
    '''

    self.thread.join(timeout)

  def get_result(self):
    '''
    Return the contents of the buffer. May be called only after the underlying
    thread has been joined.
    '''

    # FIXME to make this accessible before the thread stops, access to the
    # buffer must be synchronized so that `getvalue()` and `write()` are not
    # called at the same time, as `TextIOWrapper` classes are explicitly thread
    # un-safe: https://docs.python.org/3.6/library/io.html#multi-threading
    if self.is_alive():
      raise RuntimeError('thread must be joined before calling get_result()')
    return self._result

  def get_error(self):
    '''
    Returns an exc_info tuple if an exception was raised while reading,
    else ``None``.
    '''

    return self.thread.error

  alive = property(is_alive)
  result = property(get_result)
  error = property(get_error)

rbuffer = ReadBuffer.spawn
