import yaml
from os.path import expanduser
import sys

config_file = 'rpi-cam-mqtt.yaml'


def load_config(config_file):
    '''Open config_file and parse the yaml content'''

    try:
        # Get config from /etc
        f = open("/etc/rpi-cam-mqtt/{}".format(config_file), 'r')
    except IOError as err_conf_etc:
        try:
            # Get config from home directory
            f = open("{}/.rpi-cam-mqtt/{}".format(
                expanduser("~"),
                config_file
            ), 'r')
        except IOError as err_conf_home:
            try:
                # Get config from local directory
                f = open("./config/{}".format(config_file), 'r')
            except IOError as err_conf_local:
                print("Configuration file not found\n{}\n{]\n{}".format(
                    err_conf_etc,
                    err_conf_home,
                    err_conf_local
                ))
                sys.exit(-1)

    return yaml.load(f)
