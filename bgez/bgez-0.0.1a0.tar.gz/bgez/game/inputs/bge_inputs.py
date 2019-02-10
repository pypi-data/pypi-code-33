from typing import Optional

import abc

from bgez.core import inputs
from bgez.game import window

from bge import logic # pylint: disable=E0401

__all__ = [
    'KX_ButtonInput', 'Keyboard', 'Mouse',
    'Joystick', 'JoystickButton', 'JoystickAxis',
    'MouseDelta',
]

BGE_STATE_MAP = {
    logic.KX_INPUT_NONE: inputs.ButtonType.RELEASED,
    logic.KX_INPUT_JUST_RELEASED: inputs.ButtonType.RELEASING,
    logic.KX_INPUT_JUST_ACTIVATED: inputs.ButtonType.PRESSING,
    logic.KX_INPUT_ACTIVE: inputs.ButtonType.PRESSED,
}

class KX_ButtonInput(inputs.RawInput):

    type = inputs.ButtonType

    def __init__(self, keycode):
        self.keycode = keycode

    @abc.abstractmethod
    def _get_state(self):
        '''Returns the state of the key'''

    def value(self) -> int:
        return BGE_STATE_MAP[self._get_state()]

class Keyboard(KX_ButtonInput):
    def _get_state(self):
        return logic.keyboard.events[self.keycode]

class Mouse(KX_ButtonInput):
    def _get_state(self):
        return logic.mouse.events[self.keycode]

class Joystick:

    def __init__(self, index: int):
        self.index = index

    def get(self):
        index = self.index
        joysticks = logic.joysticks
        if index >= len(joysticks):
            return None
        return joysticks[index]

class JoystickButton(inputs.RawInput, Joystick):

    type = inputs.ButtonType

    def __init__(self, joystick: int, button: int):
        Joystick.__init__(self, joystick)
        self.button = button

    def value(self) -> Optional[int]:
        button = self.button
        joystick = self.get()
        if joystick is None:
            return None
        if button in joystick.activeButtons:
            return inputs.ButtonType.PRESSED
        return inputs.ButtonType.RELEASED

class JoystickAxis(inputs.RawInput, Joystick):

    type = inputs.AxisType

    def __init__(self, joystick: int, axis: int):
        Joystick.__init__(self, joystick)
        self.axis = axis

    def value(self) -> Optional[float]:
        axis = self.axis
        joystick = self.get()
        if (joystick is None) or (axis >= joystick.numAxis):
            return None
        return joystick.axisValues[axis]

class MouseDelta(inputs.RawInput):

    type = inputs.AxisType

    def __init__(self, axis: int):
        self.axis: int = axis
        self.bound: float = 128.

    def get(self) -> float:
        return window.mouse[self.axis]

    def value(self) -> float:
        current = self.get()
        bound = self.bound
        center = window.get_normalized_position(.5, .5)[self.axis]
        delta = (center - current) * window.size[self.axis]
        self.last = current
        return max(min(delta / bound, bound), -bound)
