from typing import NamedTuple, Optional, Tuple

from ..process import logic_process as _logic_process

from bge import logic, render # pylint: disable=E0401

__all__ = [
    'Window',
    'Screen',
    'Position',
]

class Screen(NamedTuple):
    width: int
    height: int

class Position(NamedTuple):
    x: float
    y: float

class Window(_logic_process.LogicProcess):

    __debug = {
        'framerate': render.showFramerate,
        'profile': render.showProfile,
        'properties': render.showProperties,
        'auto-debug-list': render.autoDebugList,
    }

    def __init__(self):
        self.__mouse_lock: Optional[Position] = None

    def on_post_logic(self):
        if self.__mouse_lock is not None:
            self.mouse = self.__mouse_lock

    def mouse_lock(self, position: Position = Position(.5, .5)):
        self.__mouse_lock = position

    def mouse_unlock(self):
        self.__mouse_lock = None

    def get_display(self, index: int = 0):
        return Screen(*render.getDisplayDimensions())

    def set_size(self, width: int, height: int) -> Screen:
        render.setWindowSize(width, height)
        return Screen(width, height)

    @property
    def display_count(self):
        return 1

    @property
    def displays(self):
        return tuple(self.get_display(i) for i in range(self.display_count))

    @property
    def size(self):
        return self.width, self.height

    @size.setter
    def size(self, value):
        self.set_size(*value)

    @property
    def width(self) -> int:
        return render.getWindowWidth()

    @width.setter
    def width(self, value: int) -> None:
        self.set_size(value, self.height)

    @property
    def height(self) -> int:
        return render.getWindowHeight()

    @height.setter
    def height(self, value: int) -> None:
        self.set_size(self.width, value)

    @property
    def fullscreen(self) -> bool:
        return render.getFullScreen()

    @fullscreen.setter
    def fullscreen(self, value: bool) -> None:
        render.setFullscreen(value)

    @property
    def anisotropic(self) -> bool:
        return render.getAnisotropicFilter()

    @anisotropic.setter
    def anisotropic(self, value: bool) -> None:
        render.setAnisotropicFilter(value)

    def get_normalized_position(self, x: float, y: float) -> Tuple[float, float]:
        '''
        Returns the normalized relative position in the window for `x` and `y`.
        '''
        w, h = self.width - 1, self.height - 1
        return Position(int(x * w) / w, int(y * h) / h)

    def get_mouse_position(self, format: str = '%') -> Position:
        '''
        Returns the mouse position given a format:

        >>> getMousePosition('%')
        (0.2, 1.0)
        >>> getMousePosition('px')
        (134, 2)
        '''
        position = Position(*logic.mouse.position)
        if format == '%':
            return position
        elif format == 'px':
            return Position(
                x = position.x * (self.width - 1),
                y = position.y * (self.height - 1)
            )
        raise ValueError(f'"{format}" should be one of (%, px)')

    @property
    def mouse(self) -> Position:
        return Position(*logic.mouse.position)

    @mouse.setter
    def mouse(self, value: Tuple[float, float]) -> None:
        x, y = value
        if isinstance(x, int): x /= self.width
        if isinstance(y, int): y /= self.height
        logic.mouse.position = x, y

    def screenshot(self, name: str):
        path = logic.expandPath(name)
        render.makeScreenshot(path)
        return path

    def show(self, debug: dict = {}, **kargs) -> None:
        kargs.update(debug)
        for key, value in kargs.items():
            self.__debug[key](value)
