__all__ = [
    'State',
]

class State:
    def __init__(self, enabled: bool = True):
        self._state = enabled

    def __bool__(self) -> bool:
        return self._state

    def enable(self):
        self._state = True

    def disable(self):
        self._state = False

    def toggle(self) -> bool:
        self._state = not self._state
        return self

    def set(self, enabled: bool):
        self._state = bool(enabled)
