from tap_platformpurple.streams.base import BasePlatformPurpleStream


class ProductsStream(BasePlatformPurpleStream):
    TABLE = 'products'
    KEY_PROPERTIES = ["productID"]
    API_METHOD = 'POST'

    def get_stream_data(self, data):
        return [self.transform_record(item) for item in data.get('publisherProducts')]

    def get_url(self):
        return 'https://api-v4.platformpurple.com/api/productsList/publisherOrgProductsForEnvironment'

    def get_filters(self):
        return {
            'environment': self.config.get('environment')
        }
