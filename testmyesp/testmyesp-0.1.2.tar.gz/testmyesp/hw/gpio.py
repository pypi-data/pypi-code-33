
import logging

try:
    import RPi.GPIO as rpi_gpio

except ImportError:
    rpi_gpio = None


logger = logging.getLogger(__name__)

_controller = None


class GPIOController:
    def write_output(self, gpio, value):
        raise NotImplementedError

    def read_input(self, gpio, pull=None):
        raise NotImplementedError

    def pwm_output(self, gpio, freq, duty):
        raise NotImplementedError

    def close(self):
        pass


class DummyGPIOController(GPIOController):
    def write_output(self, gpio, value):
        logger.debug('dummy GPIO: setting %s = %s', gpio, value)

    def read_input(self, gpio, pull=None):
        value = pull if pull is not None else False
        logger.debug('dummy GPIO: reading %s = %s', gpio, value)

        return value

    def pwm_output(self, gpio, freq, duty):
        logger.debug('dummy GPIO: pwm on %s = %s Hz, %s%%', gpio, freq, duty)


class RPiGPIOController(GPIOController):
    def __init__(self):
        rpi_gpio.setmode(rpi_gpio.BCM)
        rpi_gpio.setwarnings(False)
        self._pwms = {}

    def write_output(self, gpio, value):
        rpi_gpio.setup(gpio, rpi_gpio.OUT, initial=value)

    def read_input(self, gpio, pull=None):
        rpi_pull = {
            True: rpi_gpio.PUD_UP,
            False: rpi_gpio.PUD_DOWN,
            None: rpi_gpio.PUD_DOWN
        }
        rpi_gpio.setup(gpio, rpi_gpio.IN, pull_up_down=rpi_pull[pull])

        return rpi_gpio.input(gpio)

    def pwm_output(self, gpio, freq, duty):
        if gpio in self._pwms:
            self._pwms[gpio].stop()
            del self._pwms[gpio]

        if freq:
            p = rpi_gpio.PWM(gpio, freq)
            p.start(duty)

            self._pwms[gpio] = p

    def close(self):
        rpi_gpio.cleanup()


def get_gpio_controller():
    global _controller

    if _controller is None:
        if rpi_gpio:
            logger.debug('initializing RPi GPIO controller')
            _controller = RPiGPIOController()

        else:
            logger.debug('initializing dummy GPIO controller')
            _controller = DummyGPIOController()

    return _controller
