from typing import Generic, TypeVar, Optional, Union, Awaitable

import abc

from bgez.asyn import maybe_awaitable

__all__ = [
    'Resource',
]

T = TypeVar('T')

class BaseResource(Generic[T], abc.ABC):

    @abc.abstractmethod
    def load(self) -> Awaitable[T]:
        ...

    @abc.abstractmethod
    def unload(self) -> Awaitable[None]:
        ...

    @property
    @abc.abstractmethod
    def loaded(self) -> bool:
        ...

    @property
    @abc.abstractmethod
    def resource(self) -> T:
        ...

class Resource(BaseResource[T]):
    '''
    When subclassing this class, you should implement `_load` and `_unload`.\n
    '''

    def __init__(self):
        self._unloading: Awaitable[None] = None
        self._loading: Optional[Awaitable[T]] = None
        self._resource: T = None
        self._loaded: bool = False

    async def load(self) -> T:
        if self.loaded:
            return self._resource
        if self._loading is None:
            self._loading = maybe_awaitable(self._load())
        self._resource = await self._loading
        self._load_finished()
        return self._resource

    async def unload(self) -> None:
        if not self.loaded:
            return None
        if self._unloading is None:
            self._unloading = maybe_awaitable(self._unload())
        await self._unloading
        self._unload_finished()

    def _load_finished(self):
        self._loaded = True
        self._loading = None

    def _unload_finished(self):
        self._unloading = None
        self._loaded = False

    @property
    def loaded(self) -> bool:
        return self._loaded

    @property
    def resource(self) -> T:
        if self._resource is None:
            raise ValueError('resource is not loaded')
        return self._resource

    @abc.abstractmethod
    def _load(self) -> Union[T, Awaitable[T]]:
        ...

    @abc.abstractmethod
    def _unload(self) -> Union[None, Awaitable[None]]:
        ...
