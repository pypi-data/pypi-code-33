import datetime
import json
import logging
import os


class JSONLogFormatter(logging.Formatter):

    def format(self, record):
        try:
            # Parse out meesage structure if the Context logger was used
            msg = dict([[p for p in x.split('=')] for x in record.getMessage().split('; ')])
        except (ValueError, TypeError):
            # Otherwise use message as is
            msg = {'msg': record.getMessage()}
        record_dictionary = {
            'message': msg.pop('msg', None),
            'severity': record.levelname,
            'timestamp': str(datetime.datetime.fromtimestamp(float(record.created))),
            'job': msg.pop('job', None),
            'origin': msg.pop('origin', None),
            'request_id': msg.pop('request_id', None),
            'process': record.process,
            'filename': os.path.basename(record.pathname),
            'lineno': record.lineno,
            'thread': record.thread,
            'exc_info': self.formatException(record.exc_info) if record.exc_info else None
        }
        record_dictionary.update(msg)
        record_dictionary = {k:v for k,v in record_dictionary.items() if v is not None}
        return json.dumps(record_dictionary)
