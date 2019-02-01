import os

lookup = {
    'development': 'opc_app.config.DevelopmentConfig',
    'production': 'opc_app.config.ProductionConfig'
}

class Config(object):
    """Parent configuration class."""
    DEBUG = False
    CSRF_ENABLED = True

    # opc
    OPC_SERVER_HOST = 'localhost'
    OPC_SERVER_NAME = 'Kepware.KEPServerEX.V6'
    TEMPERATURE = 'XMPro.Siemens S&-1212c.Temperature'
    VIBRATION = 'XMPro.Siemens S&-1212c.Vibration'

    # logging
    LOG_DIR= '.'


class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True
    SECRET_KEY='dev'


class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = '23kjfj1n4f3iu4fio1i34fouibs'


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}