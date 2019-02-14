from collections import OrderedDict
from contextlib import suppress
from t3 import log
from t3.util import get_response_type


class DjangoFormatterMixin(log.StandardFormatter):
    def process(self, record):
        out = super().process(record)

        with suppress(AttributeError):
            # Put request id to top of log envelope
            out['request_id'] = record.request_id
            out.move_to_end('request_id', last=False)

        with suppress(AttributeError):
            # Add response info
            out['response'] = OrderedDict([
                ('status_code', record.status_code),
                ('response_type', get_response_type(record.status_code)),
                ('remote_address', record.request.getpeername()[0]),
                ('local_address', record.request.getsockname()[0]),
            ])

        return out


class DjangoFormatter(DjangoFormatterMixin, log.StandardFormatter):
    pass


class DjangoJsonFormatter(DjangoFormatterMixin, log.JsonFormatter):
    pass


class DjangoJsonPrettyFormatter(DjangoFormatterMixin, log.JsonPrettyFormatter):
    pass
