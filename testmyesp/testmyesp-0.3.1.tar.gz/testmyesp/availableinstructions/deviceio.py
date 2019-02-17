
from colibris import schemas

from testmyesp import constants

from testmyesp.hw import espctl
from testmyesp.instructions import BaseInstruction, register_instruction, InstructionException


class UnexpectedGPIOValue(InstructionException):
    def __init__(self, gpio, expected_value, read_value):
        self.gpio = gpio
        self.expected_value = expected_value
        self.read_value = read_value

    def __str__(self):
        return 'GPIO {gpio}: expected {expected}, got {read}'.format(gpio=self.gpio,
                                                                     expected=self.expected_value,
                                                                     read=self.read_value)


@register_instruction
class DevicePowerOff(BaseInstruction):
    NAME = 'device-power-off'

    def execute(self):
        espctl.power_off()


@register_instruction
class DevicePowerOn(BaseInstruction):
    NAME = 'device-power-on'

    def execute(self):
        espctl.power_on()


@register_instruction
class DeviceReset(BaseInstruction):
    NAME = 'device-reset'

    def execute(self):
        espctl.reset()


@register_instruction
class DeviceWriteGPIO(BaseInstruction):
    NAME = 'device-write-gpio'

    def __init__(self, gpio, value):
        self.gpio = gpio
        self.value = value

        super().__init__()

    def execute(self):
        espctl.write_gpio(self.gpio, self.value)

    class Schema(schemas.Schema):
        gpio = schemas.fields.Integer(validate=schemas.validate.OneOf(constants.GPIOS), required=True)
        value = schemas.fields.Boolean(required=True)


@register_instruction
class DeviceCheckGPIO(BaseInstruction):
    NAME = 'device-check-gpio'

    def __init__(self, gpio: int, value: bool):
        self.gpio = gpio
        self.value = value

        super().__init__()

    def execute(self):
        read_value = espctl.read_gpio(self.gpio)
        if read_value != self.value:
            raise UnexpectedGPIOValue(self.gpio, self.value, read_value)

    class Schema(schemas.Schema):
        gpio = schemas.fields.Integer(validate=schemas.validate.OneOf(constants.GPIOS), required=True)
        value = schemas.fields.Boolean(required=True)


@register_instruction
class DeviceWriteADC(BaseInstruction):
    NAME = 'device-write-adc'

    def __init__(self, value: int):
        self.value = value

        super().__init__()

    def execute(self):
        espctl.set_adc(self.value)

    class Schema(schemas.Schema):
        value = schemas.fields.Integer(validate=schemas.validate.Range(0, 1000), required=True)
