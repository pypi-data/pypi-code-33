from bgez.core import undefined_method

from ..process import game_process as _game_process

__all__ = [
    'RenderProcess',
]

class RenderProcess(_game_process.GameProcess):
    on_pre_draw_setup = undefined_method
    on_pre_draw = undefined_method
    on_post_draw = undefined_method
