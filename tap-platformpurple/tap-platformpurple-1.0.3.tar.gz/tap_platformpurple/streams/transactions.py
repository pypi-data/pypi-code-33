from tap_platformpurple.streams.base import BaseDatePaginatedPlatformPurpleStream


class TransactionsStream(BaseDatePaginatedPlatformPurpleStream):
    TABLE = 'transactions'
    KEY_PROPERTIES = ["transactionID"]
    API_METHOD = 'POST'

    def get_stream_data(self, data):
        return [self.transform_record(item) for item in data.get('data')]

    def get_url(self):
        return 'https://api-v4.platformpurple.com/api/stats/transactions4Org'

    def get_filters(self):
        return None
