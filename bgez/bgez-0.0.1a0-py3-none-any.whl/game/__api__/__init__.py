from .game_logic import GameLogic
from .window_manager import Window
from .scene_manager import SceneManager

__all__ = [
    'logic',
    'window',
    'scenes',
]

logic = GameLogic()
window = logic._register_manager(Window())
scenes = logic._register_manager(SceneManager())
