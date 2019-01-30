import aenum

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.4"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['BaseExtension', 'ExtensionType']


class ExtensionType(aenum.Enum):

    file = 'anji_orm.extensions.files.base.FileExtensionProtocol'


class BaseExtension:

    __slots__ = ('uri', )

    uri: str

    def __init__(self, uri: str) -> None:
        self.uri = uri

    async def async_load(self):
        pass

    def load(self):
        pass
