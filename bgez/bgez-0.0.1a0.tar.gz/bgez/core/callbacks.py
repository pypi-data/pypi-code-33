from typing import Any, NamedTuple, Optional, List

__all__ = [
    'SafeList',
    'CallbackList',
    'SilentCallbackList',
    'SilentCallbackResult',
]

class SafeList(list):

    def try_remove(self, element) -> bool:
        '''
        Tries to remove an element in the list, doesn't fail.

        Returns `True` if something was deleted, `False` otherwise.
        '''
        try:
            self.remove(element)
        except ValueError:
            return False
        return True

class CallbackList(SafeList):
    '''
    Callable list, calls every element with the same arguments.
    '''

    def __call__(self, *args, **kargs) -> List[Any]:
        return [callback(*args, **kargs) for callback in self]

class SilentCallbackResult:
    error: Optional[Exception]
    value: Optional[Any]

class SilentCallbackList(CallbackList):
    '''
    Callable list, will catch callbacks errors and output them in the end result.
    '''

    def __call__(self, *args, **kargs) -> List[SilentCallbackResult]:
        results = []
        for callback in self:
            try:
                result = SilentCallbackResult(None, callback(*args, **kargs))
            except Exception as exc:
                result = SilentCallbackResult(exc, None)
            results.append(result)
        return results
