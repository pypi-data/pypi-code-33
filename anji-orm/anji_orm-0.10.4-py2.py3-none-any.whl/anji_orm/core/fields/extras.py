import logging
from typing import Dict, Type

from jsonschema import validate

from .base import Field, DICT_ORIGIN

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.4"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['ValidableJsonField']

_log = logging.getLogger(__name__)


class ValidableJsonField(Field):

    __slots__ = ('json_scheme', )

    def __init__(self, json_scheme: Dict, **kwargs) -> None:
        super().__init__(**kwargs)
        self.json_scheme = json_scheme

    # pylint: disable=no-member
    @Field.param_type.setter  # type: ignore
    def param_type(self, value: Type) -> None:
        if value.__origin__ is DICT_ORIGIN:
            raise ValueError("Cannot use ValidableJsonField for not Dict type")
        self._param_type = value

    def __set__(self, instance, value) -> None:
        if value is not None:
            validate(value, self.json_scheme)
        super().__set__(instance, value)
