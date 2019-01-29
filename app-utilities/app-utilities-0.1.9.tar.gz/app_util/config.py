'''
Holds aplication wide configuration parameters
'''
import json
import logging
import copy
from argparse import ArgumentParser
from app_util import connections

VALID_PROFILES = ['dev', 'stage', 'prod']
LOGGER_FMT = "[%(levelname)s] [%(asctime)s] [%(name)s] - %(message)s"
LOGGER_DATE_FMT = "%m/%d/%Y %H:%M:%S"

def load_config(environment=None, config_file='config.json', argparser=None):
    '''
    Automatically loads configuration using the config file and argparser.
    First loads from the file, then command line arguments are loaded over
    the config file arguments.

    Whether or not an argparser is provided, the following arguments will be used/overidden:
    parser.add_argument('--environment', '-e', dest='environment', default='dev')
    parser.add_argument('--debug', '-d', dest='debug', action='store_true')

    returns the Namepsace object, as well as auto configured Connections object
    '''
    parser = ArgumentParser(parents=[argparser], conflict_handler='resolve') \
            if argparser else ArgumentParser()
    parser.add_argument('--environment', '-e', dest='environment', default='dev',
                        choices=VALID_PROFILES)
    parser.add_argument('--debug', '-d', dest='debug', action='store_true')
    conf, _ = parser.parse_known_args()
    environment = environment if environment in VALID_PROFILES else conf.environment
    profile_data = copy.deepcopy(conf)

    # Enable debug logging as soon as possible
    logging.basicConfig(level=logging.DEBUG if getattr(profile_data, 'debug', False) \
                                            else logging.INFO,
                        format=LOGGER_FMT, datefmt=LOGGER_DATE_FMT)
    log = logging.getLogger(__name__)
    log.debug("Debug logging enabled")

    with open(config_file) as configuration:
        try:
            config_data = json.load(configuration)
            if not isinstance(config_data, list):
                log.warning("File '%s' is not in the correct format, " \
                               + " expected a list of maps.", config_file)
            else:
                for profile in config_data:
                    if profile.get('environment') == environment:
                        profile_data.__dict__.update(profile)

        except json.decoder.JSONDecodeError:
            log.error("Could not load config file %s, check your JSON", config_file)

    profile_data.__dict__.update(conf.__dict__)
    log.info("Loaded environment: %s ", environment)

    return profile_data, connections.Connections(**profile_data.__dict__)
