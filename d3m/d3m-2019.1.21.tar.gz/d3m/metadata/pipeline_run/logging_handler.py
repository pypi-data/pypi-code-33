import logging
import typing

from d3m import utils


class LoggingHandler(logging.Handler):
    """
    Stores logging records as they are without any conversion except for:

     * formatting the logging message and adding it to the record object
     * assuring ``asctime`` is set
     * converts exception ``exc_info`` into exception's name
     * making sure ``args`` are JSON-compatible or removing it
     * making sure there are no null values
    """

    def __init__(self, callback: typing.Callable) -> None:
        super().__init__(logging.DEBUG)

        self.callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.callback(self.prepare(record))
        except Exception:
            self.handleError(record)

    def prepare(self, record: logging.LogRecord) -> typing.Dict:
        self.format(record)

        # If "asctime" is not set, we do it ourselves.
        if not hasattr(record, 'asctime'):
            if self.formatter:
                fmt = self.formatter
            else:
                fmt = logging._defaultFormatter  # type: ignore
            record.asctime = fmt.formatTime(record, fmt.datefmt)

        output = record.__dict__

        # Exceptions are not JSON compatible.
        if 'exc_info' in output:
            if output['exc_info']:
                if isinstance(output['exc_info'], BaseException):
                    output['exc_type'] = utils.type_to_str(type(output['exc_info']))
                else:
                    output['exc_type'] = utils.type_to_str(type(output['exc_info'][1]))
            del output['exc_info']

        if 'args' in output:
            try:
                output['args'] = utils.to_json_structure(output['args'])
            except Exception:
                # We assume this means "args" is not JSON compatible.
                del output['args']

        # We iterate over a list so that we can change dict while iterating.
        for key, value in list(output.items()):
            if value is None:
                del output[key]

        return output
