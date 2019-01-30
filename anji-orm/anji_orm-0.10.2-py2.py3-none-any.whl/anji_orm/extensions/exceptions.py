from anji_orm import core

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.2"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['UnsupportedExtensionConfiguration', 'RecordBindException']


class UnsupportedExtensionConfiguration(core.BaseAnjiOrmException):
    pass


class RecordBindException(core.BaseAnjiOrmException):
    pass
