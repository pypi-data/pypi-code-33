from os.path import join

from bgez import project

from .log import get_logger

__all__ = [
    'logger',
]

logger = get_logger("bgez")
logger.setLevel("DEBUG")

_logsrv = logger.add_server(join(project, "logs", "bgez.log"))
_logstream = logger.add_stream()
