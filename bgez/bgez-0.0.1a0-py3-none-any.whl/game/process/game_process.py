import abc

from bgez.core import undefined_method

__all__ = [
    'GameProcess',
]

Stopped = 0
Running = 1

class GameProcess(abc.ABC):

    _state = Stopped

    @abc.abstractmethod
    def _hook(self):
        ...

    @abc.abstractmethod
    def _unhook(self):
        ...

    @property
    def running(self):
        return self._state == Running

    def start(self) -> 'GameProcess':
        if not self.running:
            self._hook()
            self._state = Running
            self.on_start()
        return self

    def stop(self) -> 'GameProcess':
        if self.running:
            self.on_stop()
            self._unhook()
            self._state = Stopped
        return self

    on_start = undefined_method
    on_stop = undefined_method
