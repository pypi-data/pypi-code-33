import logging
import threading
from multiprocessing import Lock
from typing import Callable, TypeVar, Generic, Dict, List, Union, Tuple

T = TypeVar('T')
K = TypeVar('K')


class LRUCache(Generic[T, K]):
    __slots__ = ["_accessed_queue", "_max_size", "_queue_lock",
                 "_transaction_thread", "_data", "_in_transaction",
                 "_on_insert", "_on_update", "_on_remove", "_update_new"]

    def __init__(self, max_size: int):
        self._accessed_queue: List[K] = []
        self._max_size = max_size
        self._queue_lock = Lock()
        self._data: Dict[K, T] = {}
        self._in_transaction = False
        self._transaction_thread = None

        # Have the functions start out as None, so we can proceed and they don't take up time.
        self._update_new = False
        self._on_insert = lambda x, y: x
        self._on_update = lambda x, y: x
        self._on_remove = lambda x, y: x

        # Make sure we're in a consistent state on the way back.
        self._reset_update_new()
        self.clear_remove()
        self.clear_insert()
        self.clear_update()

    def __enter__(self):
        self.begin_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_transaction()
        return self

    def in_transaction(self):
        return self._in_transaction

    def begin_transaction(self):
        self._in_transaction = True
        self._transaction_thread = threading.current_thread()
        self._queue_lock.acquire()

    def end_transaction(self):
        self._in_transaction = False
        self._transaction_thread = None
        self._queue_lock.release()

    def compute_and_set_accessor(self, fun: Callable) -> Callable:
        def helper(key: str, *args, **kwargs) -> Union[T, None]:
            return self.compute_and_set(key, fun = fun, *args, **kwargs) # type: ignore
        return helper

    def compute_if_not_value_accessor(self, fun: Callable, stored_value: Union[T, None] = None) -> Callable:
        def helper(key: str, value: Union[T, None] = None, *args, **kwargs) -> Union[T, None]:
            if value is not None:
                return self.compute_if_not_value(key, fun = fun, value = value, *args, **kwargs) # type: ignore
            elif stored_value is not None:
                return self.compute_if_not_value(key, fun = fun, value = stored_value, *args, **kwargs) # type: ignore
            else:
                return self.compute_if_not_value(key, fun = fun, value = None, *args, **kwargs) # type: ignore
        return helper

    def compute_if_not_exists_accessor(self, fun: Callable) -> Callable:
        def helper(key: K, *args, **kwargs) -> Union[T, None]:
            return self.compute_if_not_exists(key, fun = fun, *args, **kwargs) # type: ignore
        return helper

    def compute_and_set(self, key: K, fun: Callable, *args, **kwargs):
        if not self._in_transaction or threading.current_thread() != self._transaction_thread:
            with self._queue_lock:
                return self._set(key = key, value = fun(*args, **kwargs), should_lock = False)
        else:
            return self._set(key = key, value = fun(*args, **kwargs), should_lock = False)

    def compute_if_not_value(self, key: K, value: Union[T, None], fun: Callable, *args, **kwargs) -> Union[T, None]:
        def determine_compute():
            if value is None:
                return self.compute_if_not_exists(key, fun, *args, **kwargs)
            else:
                return self.__safe_compute_if_not_value_helper(key, fun, target_val = value, *args, **kwargs)

        if not self._in_transaction:
            with self._queue_lock:
                return determine_compute()
        else:
            return determine_compute()

    def compute_if_not_exists(self, key: K, fun: Callable, *args, **kwargs) -> Union[T, None]:
        if not self._in_transaction or threading.current_thread() != self._transaction_thread:
            with self._queue_lock:
                return self.__safe_compute_if_not_value_helper(key, fun, *args, **kwargs)
        else:
            return self.__safe_compute_if_not_value_helper(key, fun, *args, **kwargs)

    def on_update(self, fun: Callable, *args, **kwargs):
        self._reset_update_new()
        self._on_update = self._get_change_func(fun, *args, **kwargs)

    def on_update_old(self, fun: Callable, *args, **kwargs):
        self._update_new = False
        self._on_update = self._get_change_func(fun, *args, **kwargs)

    def on_update_new(self, fun: Callable, *args, **kwargs):
        self._update_new = True
        self._on_update = self._get_change_func(fun, *args, **kwargs)

    def on_upsert(self, fun: Callable, *args, **kwargs):
        self.on_insert(fun, *args, **kwargs)
        self.on_update(fun, *args, **kwargs)

    def on_upsert_old(self, fun: Callable, *args, **kwargs):
        self.on_upsert(fun, *args, **kwargs)
        self._update_new = False

    def on_upsert_new(self, fun: Callable, *args, **kwargs):
        self.on_upsert(fun, *args, **kwargs)
        self._update_new = True

    def on_insert(self, fun: Callable, *args, **kwargs):
        self._on_insert = self._get_change_func(fun, *args, **kwargs)

    def on_remove(self, fun: Callable, *args, **kwargs):
        self._on_remove = self._get_change_func(fun, *args, **kwargs)

    def _reset_update_new(self):
        self._update_new = False

    def clear_insert(self):
        self._reset_update_new()
        self._on_insert = self._get_change_func(None)

    def clear_update(self):
        self._reset_update_new()
        self._on_update = self._get_change_func(None)

    def clear_remove(self):
        self._reset_update_new()
        self._on_remove = self._get_change_func(None)

    def clear_upsert(self):
        self.clear_insert()
        self.clear_update()

    def _get_change_func(self, fun, *args, **kwargs):
        def helper(key: K, value: T):
            if fun is not None:
                # Don't execute a function if we don't have one!
                fun(key, value, *args, **kwargs)
        return helper

    def get(self, key: K, default: Union[T, None] = None) -> Union[T, None]:
        return self._get(key, default, should_lock = True)

    def _get(self, key: K, default: Union[T, None] = None, should_lock = True) -> Union[T, None]:
        if key in self._data.keys():
            x = self._data.get(key)
            self._accessed_item(key, should_lock)
            return x
        else:
            return default

    def _accessed_item(self, key: K, should_lock = True) -> Tuple[Union[K, None], Union[T, None]]:
        # Don't try to reaquire the lock if already in a transaction.
        if should_lock and (not self._in_transaction or threading.current_thread() != self._transaction_thread):
            with self._queue_lock:
                return self.__safe_update_queue_helper(key)
        else:
            return self.__safe_update_queue_helper(key)

    def set_and_replace(self, key: K, value: T) -> Tuple[Union[K, None], Union[T, None]]:
        # Return the old value if it was full, could be None.
        self._set(key, value, should_lock = True)
        old_key, old_value = self._accessed_item(key, should_lock = True)
        return old_key, old_value

    def set(self, key: K, value: T) -> T:
        x = self._set(key, value)
        return x

    def _set(self, key: K, value: T, should_lock = True) -> T:
        if should_lock and (not self._in_transaction or threading.current_thread() != self._transaction_thread):
            with self._queue_lock:
                return self._safe_set(key, value)
        else:
            return self._safe_set(key, value)

    def _safe_set(self, key: K, value: T):
        self._accessed_item(key, should_lock = False)

        if not self._update_new:
            # Call the callback (with the old value)
            if key in self._data.keys():
                self._on_update(key, self._data.get(key))
            else:
                self._on_insert(key, value)

        self._data.update({key: value})

        if self._update_new:
            # Call the callback (with the new value)
            if key in self._data.keys():
                self._on_update(key, value)
            else:
                self._on_insert(key, value)

        return value

    def contains(self, key: K) -> bool:
        return self._contains(key, should_lock = True)

    def _contains(self, key: K, should_lock: bool) -> bool:
        return self._get(key, None, should_lock) is not None

    def __safe_compute_if_not_value_helper(self, key: K, fun: Callable,
                                           target_val: Union[T, None] = None, *args, **kwargs) -> Union[T, None]:
        current_val = self._get(key, should_lock = False, default = target_val)

        if (target_val is None and current_val is None) or \
                (target_val is None and target_val is not None) or \
                (target_val is not None and current_val != target_val):
            return self._set(key = key, value = fun(*args, **kwargs), should_lock = False)
        else:
            return current_val

    def __safe_update_queue_helper(self, key: K) -> Tuple[Union[K, None], Union[T, None]]:
        if len(self._accessed_queue) >= self._max_size:
            logging.debug("PQDict size exceeded, removing one element: " + str(self._max_size))
            last_key = self._accessed_queue.pop(0)
            if last_key in self._data.keys():
                last_item = self._data.pop(last_key)

                # Call the callback if it was removed from our list, on the way out.
                self._on_remove(key, last_item)
                return last_key, last_item
        else:
            # Move the key is at the beginning of the queue (the end)
            if key in self._accessed_queue:
                self._accessed_queue.remove(key)
            self._accessed_queue.append(key)

        # If we didn't remove any elements, return None for both the key and value.
        return None, None
