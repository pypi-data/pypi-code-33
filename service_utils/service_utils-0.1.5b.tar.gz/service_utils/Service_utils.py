# service requirements
import os
import logging
import argparse
import signal
import sys
import configparser
import re


class Service_utils:
    class __Service_utils:
        def __init__(
                self,
                configuration_key,
                configuration_required=False,
                configuration_default_path=None,
                description=''):

            # initialize shell arguments parser
            parser = argparse.ArgumentParser(
                description=description)
            parser.add_argument(
                configuration_key,
                metavar='path_to_configuration_file',
                required=configuration_required,
                help='Path to configuration file.')
            args = parser.parse_args()
            args = dict(args._get_kwargs())

            configuration_key = re.sub('^-+', '', configuration_key)
            configuration_key = re.sub('-', '_', configuration_key)
            configuration_path = configuration_default_path

            if configuration_required is False:
                if args[configuration_key] is None:
                    print('''
                        configuration_path is not exist and it\'s\
                        not required''')
                    print('''
                        configuration_path is set as default''')
                else:
                    configuration_path = args[configuration_key]
                    print('config is not required but it exist')
            else:
                if args[configuration_key] is None:
                    print('config is required but it doesn\'t exist')
                    raise BaseException
                else:
                    configuration_path = args[configuration_key]

            print('configuration_path:', configuration_path)
            configuration = configparser.ConfigParser()
            configuration.read(configuration_path)

            if list(configuration.keys()) == ['DEFAULT']:
                print('Bad config.')
                raise BaseException
            else:
                print('Good config.')

            self.__configuration = configuration
            self.__write_pid()
            self.__configure_logging()
            self.__set_signal_handlers()

        def get_configuration(self):
            return self.__configuration

        def __write_pid(self):
            pid_file_path = self.__configuration['pid']['pid_file_path']
            if pid_file_path is None:
                print('pid file path is None')
                return

            folders = pid_file_path.split('/')[:-1]
            pid_file_folder = '/'.join(folders)

            if not os.path.exists(pid_file_folder) and pid_file_folder != '':
                os.makedirs(pid_file_folder)
                print('{} directory made'.format(pid_file_folder))

            if pid_file_path[-4:] != '.pid':
                pid_file_path = pid_file_path + '.pid'

            with open(pid_file_path, 'w') as pid_out_file:
                pid_out_file.write('{}'.format(os.getpid()))

        def __configure_logging(self):
            # logging initializing
            try:
                logout = self.__configuration['logging']['logout']
                debug_mode = self.__configuration['logging']['debug'] == 'true'
                logging_level = logging.DEBUG if debug_mode else logging.INFO

                if logout == 'stdout' or logout == '':
                    logging.basicConfig(
                        format='\
                            \r%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S',
                        level=logging_level)
                else:
                    logging.basicConfig(
                        filename=logout, filemode='w',
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S',
                        level=logging_level)
            except BaseException:
                print('logging in not configured')
                pass

        def __set_signal_handlers(self):
            try:
                signal_codes = self.__configuration['signal_termination']
            except BaseException:
                return
            if signal_codes is None:
                return

            if signal_codes['SIGINT'] is not None:
                signal.signal(
                    signal.SIGINT,
                    lambda signal, frame: sys.exit(signal_codes['SIGINT']))

    instance = None

    def __init__(self, *args, **kwargs):
        if Service_utils.instance is None:
            Service_utils.instance = Service_utils.__Service_utils(
                *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def get_configuration(self):
        return Service_utils.instance.get_configuration()
