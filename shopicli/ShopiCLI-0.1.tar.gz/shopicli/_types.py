class ShopifyObjectBase:

    def __init__(self, data):
        self.data = data

    def __getitem__(self, name):
        return self.data[name]

    def __getattr__(self, name):
        return self.data[name]

    def __repr__(self):
        name = self.__class__.__name__
        return '{}({})'.format(name, repr(self.data))

    @classmethod
    def from_response(cls, data):
        # Allows overriding creation from an API response
        return cls(data)


class Product(ShopifyObjectBase):
    pass
