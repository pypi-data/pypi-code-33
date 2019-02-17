"""Accessible aggregate of Data documents and factory object 'build'"""

from headerindexer.data_factory._errors import ErrorsFactory as _ErrorsFactory
from headerindexer.data_factory._settings import SettingsFactory as _SettingsFactory
from headerindexer.data_factory._workings import WorkingsFactory as _WorkingsFactory
from headerindexer.data_factory._z_data_docs import SettingsDocs as _SettingsDocs, \
    ErrorsDocs as _ErrorsDocs, WorkingsDocs as _WorkingsDocs


class Settings(_SettingsDocs):
    """Schematics and docs for Settings obj"""
    pass


class Errors(_ErrorsDocs):
    pass


class Workings(_WorkingsDocs):
    pass


class _Factory(_SettingsFactory, _ErrorsFactory, _WorkingsFactory):
    """Factory to build dataclass objects. See build below for use"""


build = _Factory()
"""Importable factory to build dataclass objects"""
