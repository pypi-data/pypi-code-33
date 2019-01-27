
import logging
import time

from colibris import settings

from testmyesp.hw.gpio import get_gpio_controller


BOOT_MODE_NORMAL = 'normal'
BOOT_MODE_FLASH = 'flash'

PIN_LEVEL_DELAY = 0.2

logger = logging.getLogger(__name__)


def write_pin(func, value):
    get_gpio_controller().write_output(settings.GPIO_MAPPING[func], value)


def read_pin(func):
    return get_gpio_controller().read_input(settings.GPIO_MAPPING[func])


def initial_setup():
    logger.debug('initial setup')

    write_pin('vcc', True)
    write_pin('reset', True)
    write_pin('gpio0', False)
    write_pin('gpio2', False)
    write_pin('gpio4', False)
    write_pin('gpio5', False)
    write_pin('gpio12', False)
    write_pin('gpio13', False)
    write_pin('gpio14', False)
    write_pin('gpio15', False)
    write_pin('gpio16', False)

    get_gpio_controller().pwm_output(settings.GPIO_MAPPING['adc'], 0, 0)
    get_gpio_controller().write_output(settings.GPIO_MAPPING['adc'], False)

    time.sleep(PIN_LEVEL_DELAY)


def power_on():
    logger.debug('powering on')

    write_pin('vcc', False)
    time.sleep(PIN_LEVEL_DELAY)


def power_off():
    logger.debug('powering off')

    write_pin('vcc', True)
    time.sleep(PIN_LEVEL_DELAY)


def reset():
    logger.debug('resetting')

    write_pin('reset', False)
    time.sleep(PIN_LEVEL_DELAY)
    write_pin('reset', True)
    time.sleep(PIN_LEVEL_DELAY)


def set_boot_mode(mode):
    logger.debug('setting %s boot mode', mode)

    write_pin('gpio2', True)
    if mode == BOOT_MODE_NORMAL:
        write_pin('gpio0', True)
        write_pin('gpio15', False)

    elif mode == BOOT_MODE_FLASH:
        write_pin('gpio0', False)
        write_pin('gpio15', False)


def set_adc(value):
    value = max(0, min(1000, value))
    value = value + settings.ADC_CORRECTION_OFFS

    logger.debug('setting ADC to %s millivolts', value)
    duty = value * 100 / 3.3 / 1000

    get_gpio_controller().pwm_output(settings.GPIO_MAPPING['adc'], 0, 0)
    get_gpio_controller().write_output(settings.GPIO_MAPPING['adc'], False)
    if duty:
        get_gpio_controller().pwm_output(settings.GPIO_MAPPING['adc'], settings.PWM_FREQ, duty)


def read_gpio(gpio):
    value = read_pin('gpio' + str(gpio))
    logger.debug('read GPIO%s = %s', gpio, value)

    return value


def write_gpio(gpio, value):
    logger.debug('setting GPIO%s to %s', gpio, value)
    write_pin('gpio' + str(gpio), value)
