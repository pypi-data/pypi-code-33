import abc
from typing import Type, TYPE_CHECKING, Dict, Optional, Tuple, TypeVar, Generic, Any
from importlib import import_module
import logging

from .context import load_mark

if TYPE_CHECKING:
    # pylint: disable=unused-import
    from .model import Model
    from .register import AbstractSyncRegisterStrategy, AbstractAsyncRegisterStrategy

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["AbstractSyncExecutor", "AbstractAsyncExecutor", 'fetch']

_log = logging.getLogger(__name__)

T = TypeVar('T')


class AbstractSyncExecutor(Generic[T]):

    def __init__(self, sync_strategy: 'AbstractSyncRegisterStrategy') -> None:
        self.strategy = sync_strategy

    @abc.abstractmethod
    def send_model(self, model: 'Model') -> Dict:
        pass

    @abc.abstractmethod
    def load_model(self, model: 'Model') -> Tuple[Dict, Optional[Dict]]:
        pass

    @abc.abstractmethod
    def delete_model(self, model: 'Model') -> Dict:
        pass

    @abc.abstractmethod
    def get_model(self, model_cls: Type['Model'], id_) -> Optional['Model']:
        pass

    @abc.abstractmethod
    def execute_query(self, query: T, without_fetch: bool = False):
        pass


class AbstractAsyncExecutor(Generic[T]):

    def __init__(self, async_strategy: 'AbstractAsyncRegisterStrategy') -> None:
        self.strategy = async_strategy

    @abc.abstractmethod
    async def send_model(self, model: 'Model') -> Dict:
        pass

    @abc.abstractmethod
    async def load_model(self, model: 'Model') -> Tuple[Dict, Optional[Dict]]:
        pass

    @abc.abstractmethod
    async def delete_model(self, model: 'Model') -> Dict:
        pass

    @abc.abstractmethod
    async def get_model(self, model_cls: Type['Model'], id_) -> Optional['Model']:
        pass

    @abc.abstractmethod
    async def execute_query(self, query: T, without_fetch: bool = False):
        pass


def fetch(data_dict: Dict[str, Any], meta: Optional[Dict] = None) -> Any:
    from .register import orm_register

    fetched_dict, fetched_meta = orm_register.backend_adapter.fetch_processor(data_dict)
    if fetched_meta is not None:
        if meta is not None:
            meta.update(fetched_meta)  # type: ignore
        else:
            meta = fetched_meta
    if fetched_dict is None:
        return None
    if '_python_info' not in fetched_dict:
        # Return just this dict, if he cannot be recognized as orm model
        return fetched_dict
    module_name, class_name = fetched_dict['_python_info'].rsplit('.', 1)
    class_module = import_module(module_name)
    class_object = getattr(class_module, class_name, None)
    if class_object is None:
        _log.warning('Model record %s cannot be parsed, because class wasnt found!', fetched_dict['id'])
        return None
    fetched_dict = orm_register.backend_adapter.model_deserialization(fetched_dict, class_object)
    with load_mark():
        obj = class_object(**fetched_dict)
        obj.load(fetched_dict, meta=meta)
    return obj
