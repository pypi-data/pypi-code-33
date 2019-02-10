from bgez.core import undefined_method

from . import game_process as _game_process

__all__ = [
    'LogicProcess',
]

class LogicProcess(_game_process.GameProcess):

    def _hook(self):
        from bgez.game import logic
        logic._register_process(self)

    def _unhook(self):
        from bgez.game import logic
        logic._unregister_process(self)

    on_pre_logic = undefined_method
    on_logic = undefined_method
    on_post_logic = undefined_method
    on_exit = undefined_method
