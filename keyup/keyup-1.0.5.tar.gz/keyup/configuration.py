"""
Summary:
    local_config Module, creates local config file (json) to override default
    values set in statics module

Module Attributes:
    - current_config (TYPE str):
        JSON object resulting from parsing an existing local config file. If
        no config file exists, object is the starting seed schema stored in
        statics module
    - config_file (TYPE str):
        Path to local config file, usually found in ~/.config/PACKAGE/config.json
    - logger (TYPE logging obj):
        system logger, output set by log_mode project-level attribute
    - user_home (TYPE str):
        os-specific path to home directory determined in statics module
"""
import os
import platform
import sys
import json
import inspect
import datetime
import string
import re
from veryprettytable import VeryPrettyTable
from keyup.statics import PACKAGE, seed_config
from keyup.script_utils import export_json_object, import_file_object, read_local_config
from keyup.script_utils import stdout_message, bool_assignment, debug_mode, os_parityPath
from pyaws import Colors
from keyup import logd, __version__


try:
    from keyup.oscodes_unix import exit_codes
    os_type = 'Linux'
    splitchar = '/'                             # character for splitting paths (linux)
    text = Colors.BRIGHTCYAN
except Exception:
    from keyup.oscodes_win import exit_codes    # non-specific os-safe codes
    os_type = 'Windows'
    splitchar = '\\'                            # character for splitting paths (windows)
    text = Colors.CYAN

# universal colors
rd = Colors.RED
act = Colors.ORANGE
yl = Colors.YELLOW
fs = Colors.GOLD3
bd = Colors.BOLD
frame = text
bdwt = Colors.BOLD + Colors.BRIGHTWHITE
rst = Colors.RESET


logger = logd.getLogger(__version__)
x = VeryPrettyTable(border=True, header=False, padding_width=2)
x.align = 'c'

# globals

# current_config = local_config or seed_config    # NOTE: BOTH POPULATED AT ALL TIMES, RESOLVE
seed_file = seed_config['PROJECT']['CONFIG_PATH']
user_home = seed_config['PROJECT']['HOME']


class UpdateConfig():
    """
    Class def for parsing, update, and writing of local fs configuration file
    """

    def __init__(self, local_file, update=False, debug=False):
        """
        Summary:
            UpdateConfig will update config file if exists; else create using defaults
        Args:
            - local_file (str):
                local path incl filename of an existing configuration file
        Returns:
            TYPE: bool, update Success | Failure
        """
        self.debug = debug
        if os.path.exists(local_file):
            self.cfg_file = local_file
            self.local_config = read_local_config(local_file)
            self.parameters = self.preload_parameters(self.local_config)
            r = self.update(cfg=self.cfg_file, debug=debug)
        else:
            logger.info('local config file [%s] not found, creating using defaults.' % local_file)
            self.cfg_file = seed_config['PROJECT']['CONFIG_PATH']
            self.local_config = seed_config
            self.parameters = self.preload_parameters(seed_config)
            r = self.config_directory(cfg=self.cfg_file)
            if r:
                self.update(cfg=self.cfg_file, debug=self.debug)
        return

    def preload_parameters(self, current_config):
        """
        Summary:
            preloads existing configuration parameters or defaults if no
            local config file
        """

        params = {}

        try:
            params['enable_logging'] = current_config['LOGGING']['ENABLE_LOGGING']
            params['log_mode'] = current_config['LOGGING']['LOG_MODE']
            params['log_path'] = current_config['LOGGING']['LOG_PATH']
            params['keyage_max'] = current_config['KEY_METADATA']['KEYAGE_MAX_DAYS']
            params['keyage_min'] = current_config['KEY_METADATA']['KEYAGE_MIN_DAYS']
            params['keyage_limit'] = seed_config['KEY_METADATA']['KEYAGE_MAX_LIMIT']
            params['enable_keybackup'] = current_config['KEY_BACKUP']['BACKUP_ENABLE']
            params['backup_location'] = current_config['KEY_BACKUP']['BACKUP_LOCATION']
        except KeyError as e:
            logger.info(
                'KeyError parsing pre-existing config (%s). Replacing config file' %
                str(e))
            os.remove(self.cfg_file)
            params['enable_logging'] = seed_config['LOGGING']['ENABLE_LOGGING']
            params['log_mode'] = seed_config['LOGGING']['LOG_MODE']
            params['log_path'] = seed_config['LOGGING']['LOG_PATH']
            params['keyage_max'] = seed_config['KEY_METADATA']['KEYAGE_MAX_DAYS']
            params['keyage_min'] = seed_config['KEY_METADATA']['KEYAGE_MIN_DAYS']
            params['keyage_limit'] = seed_config['KEY_METADATA']['KEYAGE_MAX_LIMIT']
            params['enable_keybackup'] = seed_config['KEY_BACKUP']['BACKUP_ENABLE']
            params['backup_location'] = seed_config['KEY_BACKUP']['BACKUP_LOCATION']
        return params

    def update(self, cfg, debug=False):
        """ updates values in local config file """
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.print_header('update_header'))

        question = '\tType "Y" or "y" to begin. Hit return to exit config. [quit] '

        try:

            response_q0 = input(question)
            if bool_assignment(response_q0):
                # start questionnaire
                sys.stdout.write('\n')
                display_table(header='Logging', offset=38, title=True, tabspaces=8)
                sys.stdout.write(text)
                print(self.print_header('q1'))        # Question 1
                sys.stdout.write(text)
                question1 = ('\tEnable Logging? ' + rst + '[True] ').expandtabs(8)
                answer1 = (input(question1) or True)
                self.parameters['enable_logging'] = bool_assignment(answer1)
                if self.parameters['enable_logging'] not in (True, False):
                    self.parameters['enable_logging'] = converge_answer(
                        question1, [True, False], answer1)
                print(rst + '\n\tEnable Logging set to: %s\n' % self.parameters['enable_logging'])
                if self.parameters['enable_logging']:
                    # Question 1b logging
                    print(self.print_header('q2'))
                    sys.stdout.write(text)
                    question2 = (
                            '\n\tLog messages to ' + Colors.BOLD + Colors.BRIGHTWHITE +
                            'FILE' + rst + text + ', or the system logger, ' +
                            Colors.BOLD + Colors.BRIGHTWHITE + 'Syslog' + rst +
                            text + '? ' + rst + '[FILE] '
                        )
                    answer2 = (input(question2).upper() or 'FILE')
                    self.parameters['log_mode'] = converge_answer(question2, ['FILE', 'SYSLOG'], answer2)
                    #    stdout_message(msg)
                    print(rst + '\n\tLogging Mode set to: %s\n' % self.parameters['log_mode'])

                    # Q3 logging
                    if self.parameters['log_mode'] == 'FILE':
                        default = os_parityPath(self.parameters['log_path'])
                        msg = (
                                '\n\t{}Log file location? [ {} ]:  '.format(text, fs + default + text)
                            )
                        # test location to ensure write compatible
                        self.parameters['log_path'] = set_writeable_location(
                                default_location=default,
                                header=self.print_header('q3'),
                                message=msg,
                                confirmation_msg='\n\tLocal log file set to: '
                            )
                        if '.' in self.parameters['log_path'].split(splitchar)[-1]:
                            self.parameters['log_filename'] = os_parityPath(
                                    self.parameters['log_path'].split(splitchar)[-1]
                                )
                        else:
                            stdout_message(
                                message='Log file set to: %s' % os_parityPath(
                                    self.parameters['log_path'] + '/keyup.log'), tabspaces=16
                            )
                            self.parameters['log_path'] = os_parityPath(
                                self.parameters['log_path'] + '/keyup.log')
                            self.parameters['log_filename'] = 'keyup.log'
                    else:
                        # syslog chosen
                        if os_type == 'Windows':
                            stdout_message('Syslog is Unix-specific, setting logging to Windows FILE defaults')
                            self.parameters['log_mode'] = 'FILE'
                            self.parameters['log_path'] = os_parityPath(self.parameters['log_path'])
                            self.parameters['log_filename'] = 'keyup.log'
                        else:
                            self.parameters['log_path'] = '/var/log/syslog'
                            self.parameters['log_filename'] = 'syslog'
                else:
                    self.parameters['enable_logging'] = False

                # Q4:  Write Backup keysets
                sys.stdout.write('\n')
                display_table(header='Backup Keysets', offset=42, title=True, tabspaces=8)
                q4a = self.print_header('q4')
                print(q4a)
                default = self.parameters['enable_keybackup'] or False
                q4b = ('\n\tWrite Backup keyset? [%s]:  ').expandtabs(8) % (rst + str(default) + text)
                sys.stdout.write(text)
                response_q4 = input(q4b) or default
                self.parameters['enable_keybackup'] = bool_assignment(response_q4)
                if self.parameters['enable_keybackup'] not in (True, False):
                    self.parameters['enable_keybackup'] = converge_answer(
                        q4a + q4b, response_q4, [True, False])
                print(rst + '\n\tEnable key backup set to: %s\n' %
                      self.parameters['enable_keybackup'])
                if self.parameters['enable_keybackup']:
                    default = self.parameters['backup_location']
                    msg = ('\n\t{}Backup directory location? [ {} ]:  '.format(text, fs + default + text))
                    # test location to ensure write compatible
                    self.parameters['backup_location'] = set_writeable_location(
                        default_location=default,
                        header=self.print_header('q5'),
                        message=msg,
                        confirmation_msg='\n\tKeyset backup location set to: '
                    )
                    if '.' in self.parameters['backup_location'].split(splitchar)[-1]:
                        # remove it
                        extraneous_file = os_parityPath(
                            self.parameters['backup_location'].split(splitchar)[-1])
                        self.parameters['backup_location'] = os_parityPath(
                                splitchar.join(self.parameters['backup_location'].split(splitchar)[:-1])
                            )
                        stdout_message(
                            message='Removing trailing file (%s) from directory path given.' % extraneous_file,
                            tabspaces=16
                        )

                # Q6:  Key expiration
                keyage_limit = seed_config['KEY_METADATA']['KEYAGE_MAX_LIMIT']
                display_table(header='Key Expiration',  offset=42, title=True, tabspaces=8)
                print(self.print_header('q6'))

                default = self.parameters['keyage_max'] or current_config['KEY_METADATA']['KEYAGE_MAX_DAYS']
                sys.stdout.write(text)
                while True:
                    try:
                        r_q6 = input('\tEnter the number of days (1 - {} days). {}[{}]: '.format(keyage_limit, text, rst + str(default) + text)) or default
                        sys.stdout.write(text)
                        if int(r_q6) and int(r_q6) in range(1, int(keyage_limit) + 1):
                            break
                    except ValueError:
                        continue
                self.parameters['keyage_max'] = int(r_q6)
                sys.stdout.write(rst)
                print('\n\tYou selected {}{}{} days'.format(bdwt, self.parameters['keyage_max'], rst))
                print(self.print_header('closing_footer'))

            else:
                print(self.print_header('closing_footer'))
                exit_processing(exit_codes['E_USER_CANCEL']['Code'])

        except KeyboardInterrupt:
            print('\n')
            exit_processing(exit_codes['E_USER_CANCEL']['Code'])

        # process update
        debug_mode('self.parameters: ', str(self.parameters), debug)
        updated_config = self.assemble(self.parameters)
        if debug:
            logger.info(
                'updated_config (self.parameters after assembl) is: ' +
                str(updated_config)
            )
        r = self.write_config(parameter_dict=updated_config, cfg=cfg)
        return r

    def assemble(self, arg_dict):
        """
        Assembles new parameters in json format for write to new conf file
        """
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        # update version and date to current
        self.local_config['PROJECT']['CONFIG_VERSION'] = __version__
        self.local_config['PROJECT']['CONFIG_DATE'] = now

        # logging parameters
        self.local_config['LOGGING']['ENABLE_LOGGING'] = arg_dict['enable_logging']
        if arg_dict['enable_logging']:
            self.local_config['LOGGING']['LOG_MODE'] = arg_dict['log_mode']
            self.local_config['LOGGING']['LOG_FILENAME'] = arg_dict['log_filename']
            self.local_config['LOGGING']['LOG_PATH'] = arg_dict['log_path']
        self.local_config['KEY_BACKUP']['BACKUP_ENABLE'] = arg_dict['enable_keybackup']

        # key backup parameters
        if arg_dict['enable_keybackup']:
            if arg_dict.get('backup_location'):
                self.local_config['KEY_BACKUP']['BACKUP_LOCATION'] = arg_dict['backup_location']

        # key metadata
        self.local_config['KEY_METADATA']['KEYAGE_MAX_DAYS'] = arg_dict['keyage_max']
        self.local_config['KEY_METADATA']['KEYAGE_MIN_DAYS'] = arg_dict['keyage_min']
        self.local_config['KEY_METADATA']['KEYAGE_MAX_LIMIT'] = arg_dict['keyage_limit']
        return self.local_config

    def config_directory(self, cfg):
        """ Checks config_path to ensure directories exist; if not create """
        user_home = seed_config['PROJECT']['HOME']
        L1_path = user_home + splitchar + seed_config['PROJECT']['CONFIG_DIR']
        L2_path = L1_path + splitchar + seed_config['PROJECT']['CONFIG_SUBDIR']

        try:
            for path in (L1_path, L2_path):
                if not os.path.exists(path):
                    os.mkdir(path)
                    os.chmod(path, 0o700)
                    logger.info('created directory %s' % path)
                else:
                    logger.info('path exits (%s), skipping creation' % path)
        except OSError as e:
            logger.exception(
                '%s: Could not access path to configuration file. Error: %s' %
                (inspect.stack()[0][3], str(e))
            )
            return False
        return True

    def write_config(self, parameter_dict, cfg):
        """ create new config file """
        try:

            logger.info(
                '%s: writing local configuration file (%s)' %
                (inspect.stack()[0][3], cfg)
            )
            r = export_json_object(parameter_dict, filename=cfg)
            logger.info('%s: config file write complete (%s)' % (inspect.stack()[0][3], cfg))

        except OSError as e:
            logger.exception(
                '%s: Problem writing config file (%s). Error: %s' %
                (inspect.stack()[0][3], cfg, str(e)))
            return False
        return True

    def print_header(self, header):
        """ prints header strings to stdout """
        title = (
                bdwt + PACKAGE + rst + Colors.BLUE +
                ' configuration menu' + Colors.BOLD + Colors.BRIGHTWHITE
            )
        self.update_header = Colors.BOLD + Colors.BRIGHTWHITE + """
        _______________________________________________________________________

                               """ + title + """
        _______________________________________________________________________
        """ + rst + text + """
        You will be asked a series of questions which will ask you to customize
        the input values for the """ + PACKAGE + """ library or accept the global defaults.

        Press return if you wish to accept the defaults shown in brackets [] at
        the end of each question, or simply type an alternative to the default
        answer shown.
        """ + rst

        self.q1 = text + """
        Do you want to turn on logging of status messages?  Filesystem logging
        strongly recommended if you wish to automate access key rotation via a
        scheduler.

        """ + rst
        q2_title1 = Colors.BOLD + Colors.BRIGHTWHITE + 'Type 1' + rst + text
        q2_title2 = Colors.BOLD + Colors.BRIGHTWHITE + 'Type 2' + rst + text
        self.q2 = text + """
        2 types of logging are supported:

            """ + q2_title1 + """: syslog for logging to the system logger (""" + \
                    fs + """/var/log/syslog
                    """ + text + """for ubuntu and debian-based systems or """ + fs + \
                    """/var/log/messages
                    """ + text + """for redhat-based systems)

                    OR

            """ + q2_title2 + """: log to a user-specified file.  Hit return or type FILE
                    to enable this option to send log output to a location
                    on the local filesystem

        """ + rst

        self.q3 = text + """
        Please specify the filename and location in which you would like logs
        to be placed.
        """ + rst

        self.q4 = text + """
        When access keys are rotated, would you like a backup set of new keys
        written to local disk for safekeeping? By default, newly created keys
        only  exist in  your local awscli  configuration unless you choose to
        enable creation of a backup set here.
        """ + rst

        self.q5 = text + """
        When a new keyset is created, provide a writeable location on the local
        file system where you would like the backup copy of the keyset placed?
        """ + rst

        self.q6 = text + """
        How many days before an IAM keyset expires?  Keyup will show the age of
        the keyset in """ + rd + 'red' + text + """ after this duration passes.
        """ + rst

        self.closing_msg = 'This concludes configuration of local ' + bdwt + \
                            PACKAGE + rst + text + ' options.'
        self.closing_footer = bdwt + """
        _______________________________________________________________________

        """ + rst + text + """
                """ + self.closing_msg + """

        """ + rst
        return getattr(self, header)


class ReadConfig():
    def __init__(self, local_file=''):
        if os.path.exists(local_file):
            self.local_file = local_file
        else:
            logger.info('local config file [%s] not found' % local_file)
        return

    def read(self, cfg=''):
        """ reads values from local config file """
        # use parameter or
        cfg = cfg or self.local_file
        try:
            json_object = import_file_object(cfg)
            return json_object
        except IOError as e:
            logger.exception(
                '%s: Problem opening config file (%s). Error: %s' %
                (inspect.stack()[0][3], cfg, str(e))
            )
            print('Problem opening config file')
            return {}


def converge_answer(question, choices, answer=''):
    """
    Summary:
        prompt user for input until answer in appropriate responses received
    Args:
        :answer (str):  user response to question
        :choices (list):  list of valid responses. Responses are strings
    Returns:
        :valid answer (str):  valid response from choices
    """
    answer_index = []
    chars = list(string.ascii_lowercase)

    for index, response in enumerate(choices):
        entry = {chars[index]: str(response)}
        answer_index.append(entry)

    # lowercase character index (a, b, c, etc)
    keys = list(set().union(*(x.keys() for x in answer_index)))

    def print_question(index):
        """User data entry function"""
        msg = (rst + 'Please select the letter from one of the following: ')
        stdout_message(msg, tabspaces=15)
        for entry in answer_index:
            for k, v in entry.items():
                print(('\t %s:  %s' % (k, entry[k])).expandtabs(24))
        return input(('\n\t' + question + ' ').expandtabs(14))

    # get initial answer
    if not answer:
        answer = print_question(index=answer_index)

    while True:    # loop until answer in list of choices

        if answer in keys:
            return list(filter(lambda x: answer in x, answer_index))[0][answer]
            break
        elif answer in choices:
            return answer
            break
        elif not answer:    # answer blank, accept default answer between brackets
            return re.search(r"\[([A-Za-z0-9_]+)\]", question).group(1)
            break
        else:
            answer = print_question(index=answer_index)


def display_table(header, title=False, alignment='c', border=True, offset=45, tabspaces=4, color=frame):
    """Print Table Object offset from left by tabspaces"""
    padding = offset - len(header)
    table = VeryPrettyTable(border=border, header=False if title else True, padding_width=padding)
    table.align = alignment
    table.field_names = [bdwt + header + rst + frame]
    table.add_row([bdwt + header + rst + frame])

    indent = ('\t').expandtabs(tabspaces)
    table_str = table.get_string()

    for e in table_str.split('\n'):
        print(indent + color + e)
    sys.stdout.write(Colors.RESET)
    return True


def remove_trailing_slash(path):
    """
    Removes a trailing slash from provided fs path
    """
    if path[-1] in ('/', '\\'):
        path = path[:-1]
    return path


def expand_home_path(path):
    """
    Substitute ~ for actual home path
    """
    path = remove_trailing_slash(path)

    if platform.system() == 'Windows':
        return path
    try:
        user_home = os.environ['HOME']
        if path.startswith('~'):
            path = user_home + path[1:]
    except KeyError as e:
        logger.critical(
            '%s: %s variable is required and not found in the environment' %
            (inspect.stack()[0][3], str(e)))
        raise e
    return path


def validate_fs_location(path):
    """
    Summary:
        Validate existence of a path or create it
    Args:
        :path (str):
    Returns:
        Success | Failure, TYPE: bool
    """
    os_type = platform.system()

    if '.' in path.split(splitchar)[-1]:
        path = splitchar.join(path.split(splitchar)[:-1])

    test_file = path + splitchar + 'testfile.txt'
    test_msg = 'file is writeable'

    if os_type == 'Windows':
        path = os_parityPath(path)
        test_file = os_parityPath(test_file)

    try:

        if not os.path.exists(path):
            stdout_message('Creating directory path: %s' % path, tabspaces=16)
            os.makedirs(path)    # create location

        with open(test_file, 'w') as f1:
            f1.write(test_msg)

        os.remove(test_file)

    except OSError as e:
        msg = 'Location is not writeable. Retry.'
        logger.info('%s: Error %s: %s.' % (inspect.stack()[0][3], str(e), msg))
        return False
    return True


def set_writeable_location(default_location, header, message, confirmation_msg):
    """
    Summary:
        - Takes user input for filesystem location.
        - Tests to ensure location is writable
        - Removes trailing slash (if applicable)
    Args:
        :default_location (str): filesystem location if no user input
        :header (str): Header question/title to print prior to user input
        :message (str): Message to solicit user input
        :confirmation_msg (str): Display text after user input accepted
    Returns:
        :fs_location (str): writeable filesystem path
    """
    loop = True

    while loop:

        print(header); sys.stdout.write(text)

        fs_location = expand_home_path(
                input(rst + message) or default_location
            )

        # test location
        stdout_message(message='Testing write to location... ', tabspaces=16)

        r = validate_fs_location(os_parityPath(fs_location))

        if r:
            print(rst + confirmation_msg + ' ' + fs + fs_location + rst + '\n')
            loop = False
        else:
            msg = 'Location is not writeable. Retry.'
            stdout_message(message=msg, prefix='WARN', tabspaces=16)
    return fs_location


def exit_processing(code=None, clear=False):
    """Reset terminal screen colors on exit"""
    if platform.system() == 'Windows':
        os.system('color')
    if clear:
        os.system('cls' if os.name == 'nt' else 'clear')
    if code:
        sys.exit(code)
    return True


def init(debug=False, cfg=None):
    """
    Summary:
        Initiates read, write, or update of local_config file
    Args:
        :debug (bool): debug flag
        :cfg (str): path to fs object containing project k,v config parameters
    Returns:
        TYPE: bool, Success | Failure
    """
    if not cfg:

        # check default config dir for file
        default_config_path = seed_config['PROJECT']['CONFIG_PATH']

        if os.path.isfile(default_config_path):
            cfg = read_local_config(default_config_path)

    # initialize class object with default path or fs config if it exists
    init_cfg = cfg or seed_config

    if os.path.isfile(init_cfg):
        read_obj = ReadConfig(local_file=init_cfg)
        config_obj = read_obj.read(cfg=init_cfg)
        logger.info('\nCurrent config is: \n')
        logger.info(json.dumps(config_obj, indent=4))

        r = UpdateConfig(local_file=config_obj['PROJECT']['CONFIG_PATH'])

    else:
        # first time to set configuration
        r = UpdateConfig(local_file=init_cfg)

    exit_processing()
    return True

# -- end of module -----------------------------------------------------------#
