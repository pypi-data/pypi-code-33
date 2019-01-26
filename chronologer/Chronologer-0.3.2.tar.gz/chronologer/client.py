import logging


class QueueProxyHandler(logging.handlers.QueueHandler):
  '''Queue handler which creates its own ``QueueListener`` to
  proxy log records via provided ``queue`` to ``target`` handler.'''

  _listener = None
  '''Queue listener'''

  _prefix = None
  '''Global logger name prefix'''


  def __init__(self, queue, target = logging.handlers.HTTPHandler, prefix = '', **kwargs):
    self._prefix = prefix

    # user-supplied factory is not converted by default
    if isinstance(queue, logging.config.ConvertingDict):
      queue = queue.configurator.configure_custom(queue)

    super().__init__(queue)
    self._listener = logging.handlers.QueueListener(queue, target(**kwargs))
    self._listener.start()

  def close(self):
    super().close()
    self._listener.stop()

  def prepare(self, record):
    record = super().prepare(record)
    origname = record.name

    if self._prefix:
      record.name = '{}.{}'.format(self._prefix, record.name)

    if hasattr(record, 'suffix'):
      record.name = '{}.{}'.format(record.name, record.suffix)
      del record.suffix

    if record.name != origname:
      record.origname = origname

    return record

