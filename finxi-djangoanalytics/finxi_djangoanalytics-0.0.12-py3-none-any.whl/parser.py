from rest_framework.parsers import BaseParser
from urllib import parse as parser


class AnalyticsHitParser(BaseParser):
    media_type = 'text/plain'

    def parse(self, stream, media_type=None, parser_context=None):
        hits = stream.read().decode('utf-8').split('\n')
        return [self.get_first_values(parser.parse_qs(hit)) for hit in hits]

    def get_first_values(self, _dict):
        return {key: value[0] for key, value in _dict.items()}
