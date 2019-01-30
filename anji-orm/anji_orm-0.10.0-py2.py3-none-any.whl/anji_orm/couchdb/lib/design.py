import abc
from typing import Dict, Optional, Any

from .function import (
    CouchDBFilterMapFunction, CouchDBFilterFunction,
    CouchDBReduceFunction, CouchDBUpdateFunction
)

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.0"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['DesignDocView', 'DesignDocFilter', 'DesignDocUpdate']


class AbstractDesingDocElement(abc.ABC):

    __slots__ = ()

    @abc.abstractmethod
    def to_dict(self) -> Dict:
        pass


class DesignDocView(AbstractDesingDocElement):

    __slots__ = ('name', 'map_function', 'reduce_function')

    def __init__(self, name: str, map_function: CouchDBFilterMapFunction) -> None:
        self.name = name
        self.map_function: CouchDBFilterMapFunction = map_function
        self.reduce_function: Optional[CouchDBReduceFunction] = None

    def to_dict(self) -> Dict:
        base_dict: Dict[str, Any] = {
            self.name: {
                'map': self.map_function.to_javascript(),
            }
        }
        if self.reduce_function is not None:
            base_dict[self.name]['reduce'] = self.reduce_function.to_javascript()
        return base_dict

    def __eq__(self, other) -> bool:
        if not isinstance(self, DesignDocView):
            return False
        return (
            self.name == other.name and
            self.map_function == other.map_function and
            self.reduce_function == other.reduce_function
        )


class DesignDocFilter(AbstractDesingDocElement):

    __slots__ = ('name', 'filter_function')

    def __init__(self, name: str, filter_function: CouchDBFilterFunction) -> None:
        self.name = name
        self.filter_function = filter_function

    def to_dict(self) -> Dict:
        return {
            self.name: self.filter_function.to_javascript()
        }

    def __eq__(self, other) -> bool:
        if not isinstance(self, DesignDocFilter):
            return False
        return (
            self.name == other.name and
            self.filter_function == other.filter_function
        )


class DesignDocUpdate(AbstractDesingDocElement):

    __slots__ = ('name', 'update_function')

    def __init__(self, name: str, update_function: CouchDBUpdateFunction) -> None:
        self.name = name
        self.update_function = update_function

    def to_dict(self) -> Dict:
        return {
            self.name: self.update_function.to_javascript()
        }

    def __eq__(self, other) -> bool:
        if not isinstance(self, DesignDocUpdate):
            return False
        return (
            self.name == other.name and
            self.update_function == other.update_function
        )
