import logging

import rollbar

from .. import _collector


logger = logging.getLogger(__name__)


def log_errors_and_send_to_rollbar(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            logger.exception("Ranch signal error")
            rollbar.report_exc_info()
            _collector.increment("signal_error", value=1)
            raise

    return wrapper
