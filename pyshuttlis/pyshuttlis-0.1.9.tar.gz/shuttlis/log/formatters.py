import json
import logging

from .utils import _sanitize_stacktrace_for_json_fields


default_formatter = logging.Formatter(
    "[%(levelname)s -- %(asctime)s] :: (%(module)s.%(funcName)s) :: %(message)s",
    "%H:%M:%S",
)


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        json_dict = {}

        if record.exc_info:
            json_dict["stack_trace"] = _sanitize_stacktrace_for_json_fields(
                *record.exc_info
            )

            # mark exception info as none to consume the exception here and stop propogation
            # where it might get logged to sys.stderr.
            # If we need to reraise it we can log it as an exception on the root logger
            record.exc_info = None

        json_dict.update(record.__dict__)

        # Already replaced this with 'stack_trace', no longer needed
        assert json_dict["exc_info"] is None
        del json_dict["exc_info"]

        # We don't need these 2 fields as message field has msg % args now
        json_dict["message"] = record.getMessage()
        del json_dict["msg"]
        del json_dict["args"]

        json_dict["level"] = json_dict["levelname"]
        del json_dict["levelname"]

        try:
            return json.dumps(json_dict)
        except (TypeError, OverflowError):
            return json.dumps(
                {"message": "An unrecoverable exception occured while logging"}
            )
