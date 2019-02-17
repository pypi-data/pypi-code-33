
from colibris.conf.schemas import SettingsSchema, fields, register_settings_schema, validate

from testmyesp import constants


@register_settings_schema
class FlashSettingsSchema(SettingsSchema):
    FLASH_IMAGE_WRITE_TRIES = fields.Integer()
    FLASH_SIZE = fields.Integer(validate=validate.OneOf(constants.FLASH_SIZES))
    FLASH_FREQ = fields.Integer(validate=validate.OneOf(constants.FLASH_FREQS))
    FLASH_MODE = fields.String(validate=validate.OneOf(constants.FLASH_MODES))


@register_settings_schema
class SerialSettingsSchema(SettingsSchema):
    SERIAL_PORT = fields.String()
    SERIAL_FLASH_BAUD = fields.Integer(validate=validate.OneOf(constants.SERIAL_BAUD_RATES))
    SERIAL_NORMAL_BAUD = fields.Integer(validate=validate.OneOf(constants.SERIAL_BAUD_RATES))


@register_settings_schema
class ExtraSettingsSchema(SettingsSchema):
    DEVICE_SERIAL_NUMBER = fields.String()
    MAX_JOB_TIME = fields.Integer()
    PWM_FREQ = fields.Integer()
    ADC_CORRECTION_OFFS = fields.Integer()


DEBUG = True

LISTEN = '0.0.0.0'
PORT = 8888

MAX_REQUEST_BODY_SIZE = 100 * 1024 * 1024

DATABASE = {
    'backend': 'colibris.persist.SqliteDatabase',
    'name': 'testmyesp.db'
}

AUTHENTICATION = {
    'backend': 'colibris.authentication.jwt.JWTBackend',
    'model': 'testmyesp.models.Client',
    'identity_claim': 'sub',
    'identity_field': 'name',
    'secret_field': 'secret'
}

AUTHORIZATION = {
    'backend': 'colibris.authorization.role.RoleBackend',
    'role_field': 'role'
}

TASK_QUEUE = {
    'backend': 'colibris.taskqueue.rq.RQBackend',
    'host': '127.0.0.1',
    'port': 6379,
    'db': 1,
    'password': None
}

# silence queries

LOGGING_OVERRIDES = {
    'loggers': {
        'peewee': {
            'level': 'INFO'
        },
        'asyncio': {
            'level': 'INFO'
        },
        'rq': {
            'level': 'WARNING'
        }
    }
}

FLASH = {
    'image_write_tries': 2,
    'size': 1024,
    'freq': 80,
    'mode': 'dio'
}

SERIAL = {
    'port': '/dev/ttyS0',
    'flash_baud': 576000,
    'normal_baud': 115200
}

GPIO_MAPPING = {
    'gpio0': 17,
    'gpio2': 22,
    'gpio4': 23,
    'gpio5': 24,
    'gpio12': 25,
    'gpio13': 7,
    'gpio14': 8,
    'gpio15': 9,
    'gpio16': 5,
    'tx': 15,
    'rx': 14,
    'adc': 18,
    'reset': 4,
    'vcc': 2
}

WIFI_INTERFACE = 'wlan0'
START_IP = '192.168.27.50'
STOP_IP = '192.168.27.99'
HOST_IP = '192.168.27.1/24'

DEVICE_SERIAL_NUMBER = '00000000'

MAX_JOB_TIME = 300  # seconds
PWM_FREQ = 500  # hz
ADC_CORRECTION_OFFS = -30
