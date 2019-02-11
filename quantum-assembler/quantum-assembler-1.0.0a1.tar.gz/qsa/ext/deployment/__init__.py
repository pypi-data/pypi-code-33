from qsa.ext.base import BaseExtension

from .schema import ConfigSchema


class Extension(BaseExtension):
    name = 'deployment'
    schema_class = ConfigSchema
    weight = 10.0
