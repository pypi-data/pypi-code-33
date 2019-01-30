from typing import Dict, Type, Callable, Any, Optional
from datetime import datetime

import humanize

from ..core import Model

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["VerboseModel"]


class VerboseModel(Model):

    __formatters__: Dict[Optional[Type], Callable[[Any], str]] = {
        None: str,
        float: "{0:.2f}".format,
        datetime: lambda value: f"{humanize.naturaldate(value)} at {value.strftime('%H:%M:%S')}"
    }

    def to_describe_dict(self, with_internal: bool = False) -> Dict[str, str]:
        """
        Convert record to dict with pair "Pretty field name" "Pretty field value".
        By default only field with `displayed` option will be in dict.

        :param with_internal: Return all fields
        """
        fields = {}
        for field_name, field_item in self._fields.items():
            if (not field_item.internal or with_internal):
                value = getattr(self, field_name)
                if value is not None:
                    fields[field_item.description or field_item.name] = self.__formatters__.get(type(field_item.param_type), self.__formatters__[None])(value)
        return fields

    async def async_to_describe_dict(self, with_internal: bool = False) -> Dict[str, str]:
        return self.to_describe_dict(with_internal=with_internal)
