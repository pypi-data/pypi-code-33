from typing import TypeVar, Awaitable

from bgez.core import SafeList
from bgez.core.time import Scheduler, TickClock, TimeClock
from bgez.asyn import Promise, maybe_awaitable, gather

from bge.logic import ( # noqa
    expandPath,
    setGravity,
    restartGame,
    startGame,
    endGame,
    LibFree,
    LibList,
    LibLoad,
    LibNew,
)

from ..types import blend_library as _blend_library

from bgez.stubs import bge_types

T = TypeVar('T')

__all__ = [
    'GameLogic',
]

class GameLogic:

    def __init__(self):
        self.ticks = Scheduler(TickClock())
        self.time = Scheduler(TimeClock())
        self.__processes = SafeList()
        self.__managers = SafeList()

    def _register_manager(self, manager: T) -> T:
        '''Use a new manager triggered on each step.'''
        self.__managers.append(manager)
        return manager

    def _unregister_manager(self, manager: T) -> bool:
        return self.__managers.try_remove(manager)

    def _register_process(self, process: T) -> T:
        '''Use a new process triggered on each step.'''
        self.__processes.append(process)
        return process

    def _unregister_process(self, process: T) -> bool:
        return self.__processes.try_remove(process)

    def _update(self):
        self.ticks.tick()
        self.time()
        processes = self.__managers + self.__processes
        for process in processes:
            process.on_pre_logic()
        for process in processes:
            process.on_logic()
        for process in processes:
            process.on_post_logic()

    async def _exit(self):
        generator = (maybe_awaitable(process.on_exit())
            for process in self.__managers + self.__processes)
        await gather(*generator)

    def restart(self) -> None:
        '''Restarts the current game.'''
        restartGame()

    def start(self, file: str) -> None:
        '''Starts a different `.blend` file.'''
        startGame(file)

    def quit(self) -> None:
        '''Quits the game.'''
        endGame()

    @property
    def gravity(self) -> float:
        '''The game gravity setting.'''
        raise NotImplementedError

    @gravity.setter
    def gravity(self, value: float):
        setGravity(value)

    def load(self, blend_file: str, *, type: str = 'Scene') -> 'Awaitable[_blend_library.BlendLibrary]':
        '''
        Asynchronously load a blendfile.
        '''
        from bgez.game import scenes
        def libload(resolve, reject):
            status = LibLoad(expandPath(blend_file), type, asynchronous=True)
            status.onFinish = lambda status: resolve(_blend_library.BlendLibrary(scenes.current, status))
        return Promise[bge_types.LibLoadStatus](libload)

    def unload(self, path: str):
        LibFree(path)
