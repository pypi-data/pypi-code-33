"""
dcli shell
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2015-2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import argparse
import os
import sys
import logging
import shlex
from collections import OrderedDict

try:
    from prompt_toolkit import CommandLineInterface
    from prompt_toolkit.history import FileHistory, InMemoryHistory
    from prompt_toolkit.interface import AbortAction
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.shortcuts import create_prompt_application, create_eventloop
    from prompt_toolkit.styles import style_from_dict
    from prompt_toolkit.filters import Always
    from prompt_toolkit.output import DummyOutput
    from pygments.token import Token
    have_pyprompt = True
except ImportError:
    have_pyprompt = False

import six

from vmware.vapi.client.dcli.options import CliOptions
from vmware.vapi.client.dcli.util import (
    CliHelper, StatusCode, BoolAction, BoolAppendAction,
    print_top_level_help, calculate_time)
from vmware.vapi.client.dcli.exceptions import (
    handle_error, extract_error_msg, CommandCollision,
    CliArgumentException)

DCLI_COMMANDS = OrderedDict([
    ('clear', 'Clear the screen'),
    ('cls', 'Clear the screen'),
    ('exit', 'Exit the shell'),
    ('help', 'Print all shell commands'),
    ('ls', 'Print top level namespace help'),
    ('reload', 'Reload cache for CLI shell'),
    ('shell', 'Execute a shell command'),
    ('$?', 'Print return code for previous command')
])


DCLI_SKIP_PREFIX = 'com.vmware'

logger = logging.getLogger(__name__)

if have_pyprompt:
    def get_secure_history_string(string, completer):
        """
        Helper function which expands short command and returns it back
        with securely escaped argument input
        """
        exp_cmd = completer.expand_short_command(string)
        is_command, secret_map = completer.cli_main.get_command_secret_map(exp_cmd.split())
        if is_command and secret_map:
            exp_cmd = completer.cli_main.get_secure_command(exp_cmd.split(),
                                                            secret_map,
                                                            substitute='')
            string_arg_index = string.find('-') if string.find('-') > -1 else string.find('+')
            exp_cmd_arg_index = exp_cmd.find('-') if exp_cmd.find('-') > -1 else exp_cmd.find('+')
            if string_arg_index > -1 and exp_cmd_arg_index > 1:
                string = string[:string_arg_index] + exp_cmd[exp_cmd_arg_index:]
        return string

    class DcliFileHistory(FileHistory):
        """
        Overwrites prompt_toolkit FileHistory class to secure saved history
        """
        def __init__(self, filename, completer):  # pylint: disable=E1002
            self.completer = completer
            super(DcliFileHistory, self).__init__(filename)

        def append(self, string):  # pylint: disable=E1002
            """
            Append's given command string to history
            """
            string = get_secure_history_string(string, self.completer)
            super(DcliFileHistory, self).append(string)

    class DcliInMemoryHistory(InMemoryHistory):
        """
        Overwrites prompt_toolkit InMemoryHistory class to secure in-memroy preserved history
        """
        def __init__(self, completer):  # pylint: disable=E1002
            self.completer = completer
            super(DcliInMemoryHistory, self).__init__()

        def append(self, string):  # pylint: disable=E1002
            """
            Append's given command string to history
            """
            string = get_secure_history_string(string, self.completer)
            super(DcliInMemoryHistory, self).append(string)

    class PypromptCompleter(Completer):
        """
        Class to auto complete dcli commands and options in interactive mode
        """
        def __init__(self, cli_main, prompt):
            self.cli_main = cli_main
            self.prompt = prompt
            self.current_cmd = None
            self.cmd_args = []
            self.history = None

            self.set_prompt_history()

        def set_prompt_history(self):
            """
            Sets prompt history
            """
            if not os.path.exists(CliOptions.DCLI_HISTORY_FILE_PATH):
                self.history = DcliFileHistory(CliOptions.DCLI_HISTORY_FILE_PATH, self)
            elif not os.access(CliOptions.DCLI_HISTORY_FILE_PATH, os.R_OK):
                warning_msg = ("WARNING: No read permissions for history file '%s'.\n"
                               "Switching to in-memory history.") % (CliOptions.DCLI_HISTORY_FILE_PATH)
                logger.warning(warning_msg)
                print(warning_msg)
                self.history = DcliInMemoryHistory(self)
            elif not os.access(CliOptions.DCLI_HISTORY_FILE_PATH, os.W_OK):
                warning_msg = ("WARNING: No write permissions for history file '%s'.\n"
                               "Switching to in-memory history.") % (CliOptions.DCLI_HISTORY_FILE_PATH)
                logger.warning(warning_msg)
                print(warning_msg)
                self.history = DcliInMemoryHistory(self)
            else:
                self.history = DcliFileHistory(CliOptions.DCLI_HISTORY_FILE_PATH, self)

        @staticmethod
        def get_dcli_options(curr_key):
            """
            Method to return the dcli '+' options for auto completion

            :type   curr_key: :class:`string`
            :param  curr_key: Current typed key in interactive mode
            """
            return OrderedDict((option.name, option.description) for option in CliOptions.get_interactive_parser_plus_options()
                               if option.name.startswith(curr_key) and option.description != argparse.SUPPRESS)

        @staticmethod
        def sort_options(options):
            """
            Sort auto complete dcli options
            """
            sorted_options = sorted(options, key=lambda t: t[0])
            sorted_options = sorted(sorted_options, key=lambda t: t[2])
            return OrderedDict((option[0], option[1]) for option in sorted_options)

        def get_command_args(self, command):
            """
            Method to get input arguments struct for a command

            :type  command: :class:`string`
            :param command: vAPI command

            :rtype:  :class:`list` of :class:`ArgumentInfo`
            :return: List of ArgumentInfo object containing struct field details
            """
            self.cmd_args = []
            self.current_cmd = None
            path = command.rpartition('.')[0]
            name = command.split('.')[-1]
            cli_cmd_instance = self.cli_main.get_cmd_instance(path, name)

            if cli_cmd_instance and cli_cmd_instance.is_a_command():
                try:
                    retval, args = cli_cmd_instance.get_parser_arguments()
                except Exception:
                    retval = StatusCode.INVALID_COMMAND

                if retval == StatusCode.SUCCESS:
                    self.current_cmd = command
                    self.cmd_args = args

        def prepare_autocomplete_map(self, completer_root_key):
            """
            Alters the complete command map depending on whether
            completer_root_key contains one of the hidden namespace's name

            :type  completer_root_key: :class:`str`
            :param completer_root_key: command written on prompt so far

            :rtype:  :class:`list`
            :return: Updated command map completer
            """
            for hidden_ns in CliOptions.DCLI_HIDDEN_NAMESPACES:
                if hidden_ns['name'] and hidden_ns['name'] in completer_root_key or \
                        (not hidden_ns['name'] and hidden_ns['path'] in completer_root_key):
                    self.cli_main.cmd_map.update(self.cli_main.hidden_cmd_map)
                    break
            else:  # executed if no break or exception reached in the loop
                for key in self.cli_main.hidden_cmd_map:
                    self.cli_main.cmd_map.pop(key, None)

        def call_shell_commands(self, command):
            """
            Method to call special dcli interactive mode commands

            :type  command: :class:`str`
            :param command: dcli command

            :rtype:  :class:`StatusCode`
            :return: Status code
            """
            status = StatusCode.SUCCESS
            if command.lower() in ['clear', 'cls']:
                if os.name == 'nt':  # call cls for windows systems.
                    os.system('cls')
                else:
                    os.system('clear')
            elif command.lower() in ['ls']:
                status = self.cli_main.handle_command('', '')
            elif command == '$?':
                print(status)
            elif command.lower() == 'reload':
                self.cli_metadata.cache_cli_metadata(self.cli_main.connections)
            elif command.lower() == 'help':
                print('\t'.join(DCLI_COMMANDS.keys()))
            elif command.split()[0] == 'shell':
                import signal
                import subprocess

                def _handler(_sig, _frame):
                    """
                    Interrupt handler for shell command
                    """
                    p.terminate()
                    p.communicate()

                if len(command.split()) == 1:
                    handle_error('Missing shell command that needs to be '
                                 'executed')
                    status = StatusCode.INVALID_COMMAND
                    return status

                logger.info('Invoking shell command: %s', command)
                command = command.split()[1:]
                try:
                    p = subprocess.Popen(command, stdin=sys.stdin, stdout=sys.stdout, shell=False)
                except OSError as e:
                    error_msg = 'Command %s failed with: %s' % (' '.join(command), extract_error_msg(e))
                    handle_error(error_msg, exception=e)
                    status = StatusCode.INVALID_COMMAND
                    return status

                old_handler = signal.signal(signal.SIGINT, _handler)
                status = StatusCode.INVALID_COMMAND
                try:
                    status = p.wait()
                except OSError as e:
                    error_msg = 'Command %s terminated.' % ' '.join(command)
                    handle_error(error_msg, exception=e)
                finally:
                    signal.signal(signal.SIGINT, old_handler)

            return status

        def expand_short_command(self, command, throw=False):
            """
            Method to expand short commands
            """
            orig_command = command

            # Check if user entered 'short' version of the command
            arg_list = command.split()
            arg_index = [i for i, x in enumerate(arg_list) if x.startswith('-') or x.startswith('+')]
            index = len(arg_list) if not arg_index else arg_index[0]
            key = '.'.join(arg_list[0:index])
            dcli_commands = [cmd for cmd in self.cli_main.cmd_list if key in cmd]
            collected_collisions = []

            if not dcli_commands:
                command = orig_command
            elif len(dcli_commands) > 1:
                # Check if one of the possible command option matches the full
                # command name specified by the user.
                search_name = '.%s' % '.'.join(arg_list[0:index])
                matched_cmd = [cmd for cmd in dcli_commands if cmd.endswith(search_name)]
                if len(matched_cmd) == 1:
                    command = ' '.join(matched_cmd[0].split('.') + arg_list[index:])
                else:
                    # if more than two namespaces found for short cmd collect them to throw correct error later
                    if len(matched_cmd) > 1:
                        collected_collisions = collected_collisions + matched_cmd
                    dcli_commands = [ns for ns in self.cli_main.ns_list if ns.endswith(search_name)]
                    if dcli_commands and len(dcli_commands) == 1:
                        command = ' '.join(dcli_commands[0].split('.') + arg_list[index:])
                    elif dcli_commands and len(dcli_commands) > 1:  # more than two commands found for short cmd
                        collected_collisions = collected_collisions + dcli_commands
                    else:
                        command = orig_command
            else:
                if dcli_commands[0].endswith(key):  # case if the short cmd expands to vapi command
                    command = ' '.join(dcli_commands[0].split('.') + arg_list[index:])
                else:  # case if short cmd expands to vapi namepsace
                    namespace_cmd_idx_end = dcli_commands[0].index(key) + len(key)
                    namespace_cmd = dcli_commands[0][0:namespace_cmd_idx_end]
                    command = ' '.join(namespace_cmd.split('.') + arg_list[index:])

            if throw and collected_collisions:
                converted_collected_collisions = [command.replace('.', ' ') for command in collected_collisions]
                error_msg = "The command you are trying to execute is " \
                            "ambiguous. You can execute one of the " \
                            "following commands:\n"
                error_msg += '\n'.join(converted_collected_collisions)
                exception = CommandCollision(converted_collected_collisions,
                                             error_msg)
                handle_error(error_msg, prefix_message='')
                raise exception
            return command

        def get_completions(self, document, _):
            """
            Return possible auto completion value and handle errors to does not cause crash
            """
            try:
                # can not use 'yield from' since it's illegal statement on python 2.7
                for item in self.get_unhandled_completions(document):
                    yield item
            except Exception as e:
                handle_error('Auto complete error occured: {}'.format(str(e)), print_error=False, exception=e)
                yield Completion('', display='Error: Cannot autocomplete command.')

        def complete_pyprompt_command_options(self, tokens, root_key, curr_key):
            """
            Method to get matches for vAPI command options and values

            :type  token: :class:`string`
            :param token: Complete token string entered on interactive shell
            :type  root_key: :class:`string`
            :param root_key: Root key
            :type  curr_key: :class:`string`
            :param curr_key: Current key
            """
            match_dict = OrderedDict()
            choices = []
            # This is probably a vAPI command, try to get command options.
            key = root_key.split('--')[0].rstrip('.')
            key = key.split('+')[0].rstrip('.')
            exp_cmd = self.expand_short_command(key)
            commands = ['.'.join(exp_cmd.split())]

            split_tokens = tokens.rsplit()

            # if the command changed from the last command read args again
            if commands[0] != self.current_cmd:
                self.get_command_args(commands[0])

            prev_token = split_tokens[-2] if curr_key else split_tokens[-1]
            prev_arg = [arg for arg in self.cmd_args if arg.name == prev_token]

            # if the previous option is a valid option and is not a flag/secret
            # option then complete the option value if possible
            if (prev_arg and prev_arg[0].nargs != '?'
                    or prev_token in ['+formatter', '+loglevel']):

                if (prev_arg and (prev_arg[0].arg_action == BoolAction
                                  or prev_arg[0].arg_action == BoolAppendAction)):
                    choices = ['true', 'false']
                elif prev_arg:
                    choices = prev_arg[0].choices
                elif prev_token == '+formatter':
                    choices = CliOptions.FORMATTERS
                elif prev_token == '+loglevel':
                    choices = CliOptions.LOGLEVELS

                if choices:
                    choices = sorted(choices)
                    if curr_key:
                        match_dict = OrderedDict((choice, '') for choice in choices
                                                 if choice.startswith(curr_key))
                    else:
                        match_dict = OrderedDict((choice, '') for choice in choices)
            else:
                temp_list = []
                # If it's not an option value then give find the list of possible options
                # for this command - after removing already entered optioned on prompt.
                if commands[0] != self.current_cmd:
                    if curr_key:
                        temp_list = [(arg.name, arg.description, not arg.required) for arg in self.cmd_args
                                     if arg.name.startswith(curr_key)]
                    else:
                        temp_list = [(arg.name, arg.description, not arg.required) for arg in self.cmd_args]
                else:
                    if curr_key:
                        temp_list = [(arg.name, arg.description, not arg.required) for arg in self.cmd_args
                                     if ((tokens.find(' ' + arg.name + ' ') == -1
                                          or arg.arg_action == 'append'
                                          or arg.arg_action == BoolAppendAction)
                                         and arg.name.startswith(curr_key))]
                    else:
                        temp_list = [(arg.name, arg.description, not arg.required) for arg in self.cmd_args
                                     if tokens.find(' ' + arg.name + ' ') == -1
                                     or arg.arg_action == 'append'
                                     or arg.arg_action == BoolAppendAction]

                # Return sorted list of command matches
                match_dict = PypromptCompleter.sort_options(temp_list)

            return match_dict

        def get_unhandled_completions(self, document):
            """
            Return possible auto completion value
            """
            location = 0
            match_dict = OrderedDict()
            tokens = document.text_before_cursor
            search_text = tokens.replace(' ', '.')
            begin, _ = document.find_boundaries_of_current_word(WORD=True)

            # This is not the first word on the prompt
            if search_text.find('.') != -1:  # pylint: disable=too-many-nested-blocks
                word_index = len(
                    search_text) + begin  # begin gives negative index from current position

                # Get the previous and current tokens on the command line.
                root_key = search_text[:word_index].rstrip('--').rstrip('.')
                if root_key:  # root_key should not be empty
                    curr_key = search_text[word_index:]
                    self.prepare_autocomplete_map(root_key)

                    # If there's no current token text, start of a fresh token
                    if not curr_key:
                        commands = []
                        # Try to find a match for prev tokens in cmd map
                        for cmd in six.iterkeys(self.cli_main.cmd_map):
                            if root_key in cmd:
                                split_match = cmd.split(root_key)[-1]
                                if split_match and not split_match.startswith('.'):
                                    continue
                                temp_match = split_match.lstrip('.').split('.')[0]
                                if temp_match:
                                    commands.append((temp_match,
                                                     self.cli_main.ns_cmd_info.get(cmd, ('', True))))
                                else:
                                    commands += \
                                        [(i_cmd, self.cli_main.ns_cmd_info.get('%s.%s' % (cmd, i_cmd), ('', True)))
                                         for i_cmd in self.cli_main.cmd_map[cmd]]
                        if commands:
                            match_dict = OrderedDict(
                                (cmd, descr) for cmd, descr in commands)
                        else:
                            # If no match found check if it's a command and return options
                            match_dict = self.complete_pyprompt_command_options(
                                tokens, root_key, curr_key)
                    else:
                        # Special check to auto-complete '+' options
                        if curr_key.startswith('+'):
                            match_dict = PypromptCompleter.get_dcli_options(
                                curr_key)
                        else:
                            commands = []
                            for cmd in six.iterkeys(self.cli_main.cmd_map):
                                if root_key in cmd:
                                    temp_match = \
                                        cmd.split(root_key)[-1].lstrip('.').split('.')[0]
                                    if temp_match:
                                        commands.append((temp_match,
                                                         self.cli_main.ns_cmd_info.get(
                                                             cmd, ('', True))))
                                    else:
                                        commands += \
                                            [(i_cmd, self.cli_main.ns_cmd_info.get('%s.%s' % (cmd, i_cmd), ('', True)))
                                             for i_cmd in self.cli_main.cmd_map[cmd]]
                            if commands:
                                match_dict = OrderedDict(
                                    (cmd, descr) for cmd, descr in commands if
                                    cmd.startswith(curr_key))
                            else:
                                # If no match found check if it's a command and return options
                                match_dict = self.complete_pyprompt_command_options(
                                    tokens, root_key, curr_key)
            else:
                # First word on the prompt
                if not search_text:
                    # First tab on the prompt (no text present)
                    match_dict = OrderedDict(
                        (cmd.replace('.', ' '), self.cli_main.ns_cmd_info[cmd])
                        for cmd in six.iterkeys(self.cli_main.cmd_map)
                        if cmd == DCLI_SKIP_PREFIX)
                elif search_text.startswith('+'):
                    # Special check to auto-complete '+' options
                    match_dict = PypromptCompleter.get_dcli_options(search_text)
                else:
                    match_dict = OrderedDict((path,
                                              self.cli_main.ns_cmd_info.get(cmd, ('', True)))
                                             for cmd in
                                             six.iterkeys(self.cli_main.cmd_map)
                                             if search_text in cmd
                                             for path in cmd.split('.')
                                             if path.startswith(search_text))

                    for key, value in DCLI_COMMANDS.items():
                        if key.startswith(search_text):
                            match_dict[key] = value

            # Calculate where to insert found match on the prompt
            if tokens and tokens[-1] == ' ':
                location = 0
            elif tokens:
                word_before_cursor = tokens.strip().split()[-1]
                location = -len(word_before_cursor)

            if not match_dict:
                # If no match found, put location as 0 to not delete any
                # input typed by user
                yield Completion('', start_position=0, display='',
                                 display_meta='')
            else:
                for key, value in match_dict.items():
                    display = key
                    description = value
                    if isinstance(value, tuple):
                        description = value[0]
                        if value[1]:
                            display = '> %s' % key
                    yield Completion(key, start_position=location,
                                     display=display, display_meta=description)


class CliShell(object):
    """
    Class to open and manage a CLI shell
    """
    def __init__(self, cli_main, prompt=CliOptions.PROMPT_DEFAULT_VALUE):
        """
        CLI shell class init method

        """
        self.prompt = prompt
        self.cli_main = cli_main
        self.cli = None
        if have_pyprompt:
            self.completer = PypromptCompleter(self.cli_main, prompt)
        else:
            self.completer = None

    def get_cli_shell(self, input_=None):
        """
        Method to get cli shell object

        """
        if not have_pyprompt:
            return

        style = CliShell.get_cli_prompt_style()
        application = create_prompt_application(message=self.prompt,
                                                history=self.completer.history,
                                                completer=self.completer,
                                                complete_while_typing=Always(),
                                                auto_suggest=AutoSuggestFromHistory(),
                                                style=style,
                                                on_abort=AbortAction.RETRY)
        if input_:
            self.cli = CommandLineInterface(application=application,
                                            eventloop=create_eventloop(),
                                            input=input_,
                                            output=DummyOutput())
        else:
            self.cli = CommandLineInterface(application=application,
                                            eventloop=create_eventloop())

    def get_shell_parser(self):
        """
        Initializes and returns shells' argparse parser

        :rtype:  :class:`CliArgParser`
        :return: CliArgParser object
        """
        parser = CliHelper.get_parser(True)

        # show top level help for one of the available connections
        # doesn't make sense to 'spam' with all
        server_type = None
        if self.cli_main.connections:
            server_type = self.cli_main.connections[0].server_type
        print_top_level_help(True, server_type)

        return parser

    @staticmethod
    def get_cli_prompt_style():
        """
        Returns cli prompt style. Defaults to gray color theme for the
        autocompletion. If environment variable DCLI_COLOR_THEME is set,
        its value is used to change the default theme. Currently supporting
        Blue, Green, Red, and Yellow values.

        :return: prompt toolkit style dictionary which specifies the style to
         be applied to the autocompletion prompt or None
        :rtype: :class:`prompt_toolkit.styles.from_dict._StyleFromDict` or None
        """
        theme_name = CliOptions.DCLI_COLOR_THEME.lower()

        if theme_name == '':
            font_color = '#ffffff'
            font_color_selected = '#000000'
            font_color_meta = '#000000'
            completion_color_selected = '#00aaaa'
            completion_color = '#008888'
            meta_color = '#949494'
            meta_color_selected = '#a8a8a8'
            progress_btn_color = '#003333'
        elif theme_name == 'blue':
            font_color = '#ffffff'
            font_color_selected = '#000000'
            font_color_meta = '#ffffff'
            completion_color_selected = '#0099cc'
            completion_color = '#007399'
            meta_color = '#0093b9'
            meta_color_selected = '#0099cc'
            progress_btn_color = '#006080'
        elif theme_name == 'red':
            font_color = '#ffffff'
            font_color_selected = '#000000'
            font_color_meta = '#ffffff'
            completion_color_selected = '#dd0000'
            completion_color = '#7c0000'
            meta_color = '#9c0000'
            meta_color_selected = '#dd0000'
            progress_btn_color = '#550000'
        elif theme_name == 'green':
            font_color = '#ffffff'
            font_color_selected = '#000000'
            font_color_meta = '#ffffff'
            completion_color_selected = '#14b814'
            completion_color = '#0a5c0a'
            meta_color = '#0f8a0f'
            meta_color_selected = '#14b814'
            progress_btn_color = '#005500'
        elif theme_name == 'yellow':
            font_color = '#ffffff'
            font_color_selected = '#000000'
            font_color_meta = '#ffffff'
            completion_color_selected = '#bbbb00'
            completion_color = '#666600'
            meta_color = '#999900'
            meta_color_selected = '#bbbb00'
            progress_btn_color = '#555500'
        elif theme_name in ['gray', 'grey']:
            font_color = '#000000'
            font_color_selected = '#ffffff'
            font_color_meta = '#000000'
            completion_color_selected = '#878787'
            completion_color = '#bcbcbc'
            meta_color = '#949494'
            meta_color_selected = '#a8a8a8'
            progress_btn_color = '#444444'
        else:
            warning_msg = 'Invalid color theme "%s". Switching to ' \
                          'default one - gray' % CliOptions.DCLI_COLOR_THEME
            logger.warning(warning_msg)
            print(warning_msg)
            return None

        styles_dict = {}
        styles_dict[Token.Menu.Completions.Completion.Current] = \
            'bg:%s %s bold' % (completion_color_selected, font_color_selected)
        styles_dict[Token.Menu.Completions.Completion] = \
            'bg:%s %s' % (completion_color, font_color)
        styles_dict[Token.Menu.Completions.Meta.Current] = \
            'bg:%s %s' % (meta_color_selected, font_color)
        styles_dict[Token.Menu.Completions.Meta] = \
            'bg:%s %s' % (meta_color, font_color_meta)
        styles_dict[Token.Scrollbar.Button] = \
            'bg:%s' % progress_btn_color
        styles_dict[Token.Scrollbar] = \
            'bg:%s' % completion_color_selected

        return style_from_dict(styles_dict)

    def execute_vapi_command(self, parser, command, fp=sys.stdout):
        """
        Method to execute vapi command

        :type  parser: :class:`CliArgParser`
        :param parser: CliArgParser class instance
        :type  command: :class:`str`
        :param command: vAPI command to execute
        :type  fp: :class:`File`
        :param fp: Output file stream
        """
        exp_command = self.completer.expand_short_command(command, True)
        split_cmd = None

        # For interactive mode we have to do quote handling
        # Use shlex for POSIX while for windows do manually
        if os.name == 'nt':
            split_cmd = CliHelper.get_cli_args(exp_command)
        else:
            if six.PY2:
                tmp_cmd = shlex.split(exp_command.encode('utf-8'))
                split_cmd = [c.decode('utf-8') for c in tmp_cmd]
            else:
                split_cmd = shlex.split(exp_command)

        return self.cli_main.process_input(split_cmd, parser, fp=fp)

    def run_shell(self, first_command=None, fp=sys.stdout):
        """
        Method to display CLI shell and process commands

        """
        parser = self.get_shell_parser()
        self.get_cli_shell()
        status = StatusCode.SUCCESS

        while True:
            if not first_command:
                try:
                    command = self.get_command()
                except EOFError as e:
                    error_msg = 'Exiting %s shell' % CliOptions.CLI_CLIENT_NAME
                    handle_error(error_msg, exception=e)
                    return status
                except KeyboardInterrupt:
                    print()
                    continue
            else:
                command = first_command
                first_command = None
                print()  # breaker line between first command and welcome message
            self.cli_main.current_dcli_command = command

            if not command:
                continue
            elif command.split()[0].lower() in DCLI_COMMANDS:
                if command.rstrip().lower() == 'exit':
                    return status
                else:
                    status = calculate_time(lambda: self.completer.call_shell_commands(command.rstrip()),
                                            'shell command execution time',
                                            self.cli_main.current_dcli_command)
            else:
                try:
                    status = calculate_time(lambda: self.execute_vapi_command(parser, command, fp=fp),
                                            'full command execution time',
                                            self.cli_main.current_dcli_command)
                except CommandCollision as e:
                    pass
                except KeyboardInterrupt as e:
                    status = StatusCode.INVALID_COMMAND
                    error_msg = 'Execution of command "%s" interrupted' % command
                    handle_error(error_msg, exception=e)
                except CliArgumentException as e:
                    status = e.status_code
                    if e.print_error:
                        handle_error(e.msg, exception=e)
                except Exception as e:
                    status = StatusCode.INVALID_COMMAND
                    error_msg = 'Error executing command "%s"' % command
                    handle_error(error_msg)
                    msg = extract_error_msg(e)
                    if msg:
                        handle_error(msg, exception=e)

            if self.should_exit_shell():
                break

        return status

    def get_command(self):
        """
        Gets command string
        Note: Used to be patched by testing infrastructure

        :return: command string
        :rtype: :class:`str`
        """
        document = self.cli.run(True)
        return document.text

    def should_exit_shell(self):  # pylint: disable=R0201
        """
        Checks whether to exit shell mode
        Note: Used to be patched by testing infrastructure

        :return: whether to exit shell mode
        :rtype: :class:`bool`
        """
        return False
