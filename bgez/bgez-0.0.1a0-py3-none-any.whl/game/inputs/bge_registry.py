import re

from bgez.game import inputs

import bge # pylint: disable=E0401

__all__ = [
    'BGE_INPUT_REGISTRY',
]

JOYSTICK_MAX_COUNT = 8
JOYSTICK_MAX_BUTTONS = 32
JOYSTICK_MAX_AXIS = 8

def _create_bge_input_registry():
    registry = {}

    pattern = re.compile(r'key$')

    # mouse/keyboard buttons
    for name in dir(bge.events):
        keycode = getattr(bge.events, name)

        if not isinstance(keycode, int):
            continue # not a keycode

        key = pattern.sub('', name.lower())

        if keycode in bge.logic.keyboard.events:
            input = inputs.Keyboard(keycode)
        elif keycode in bge.logic.mouse.events:
            input = inputs.Mouse(keycode)
        else: continue

        registry[key] = input

    # mouse axis
    registry['mouse.dx'] = inputs.MouseDelta(0)
    registry['mouse.dy'] = inputs.MouseDelta(1)

    # joysticks
    for joystickIndex in range(JOYSTICK_MAX_COUNT):
        joystickName = f'joystick{joystickIndex}'

        # joysticks buttons
        for buttonIndex in range(JOYSTICK_MAX_BUTTONS):
            inputName = f'{joystickName}.button{buttonIndex}'
            registry[inputName] = inputs.JoystickButton(joystickIndex, buttonIndex)

        # joysticks axis
        for axisIndex in range(JOYSTICK_MAX_AXIS):
            inputName = f'{joystickName}.axis{axisIndex}'
            registry[inputName] = inputs.JoystickAxis(joystickIndex, axisIndex)

    return registry

BGE_INPUT_REGISTRY = _create_bge_input_registry()
