__all__ = [
    'Toggle',
]

class Toggle:
    '''
    Toggleable instance, act as a boolean.
    '''

    def __init__(self, state: bool = False):
        self.set(state)

    def __bool__(self) -> bool:
        return self._state

    def set(self, state: bool) -> bool:
        self._state = bool(state)
        return self._state

    def toggle(self) -> bool:
        '''
        Toggles the state of the instance.
        Returns the new state.
        '''
        new = self._state = not self
        return new

    def __invert__(self):
        return not self
