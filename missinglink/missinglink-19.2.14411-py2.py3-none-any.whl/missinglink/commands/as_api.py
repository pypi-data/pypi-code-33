# -*- coding: utf8 -*-
import json
import click


class ApiException(Exception):
    pass


class InvalidJsonOutput(Exception):
    pass


class _ApiCall:
    def __init__(self, cli, command_cli, *commands, **kwargs):
        self._cli = cli
        self._commands = commands
        config_file = kwargs.pop('config_file', None)
        self._config_file = config_file
        self._command_cli = command_cli

    def __call__(self, *args, **kwargs):
        return self._run(*args, **kwargs)

    def _get_param(self, name):
        for param in self._command_cli.params:
            if name in param.opts or name in param.secondary_opts:
                return param

    @classmethod
    def __make_arg_list(cls, key, val, param):
        if isinstance(val, (list, tuple)):
            if len(val) > 1 and not param.multiple:
                raise AttributeError('parameter %s does not support multiple' % (key,))

            return val

        return [val]

    def __validate_param(self, key, flag):
        param = self._get_param(flag)

        if param is None:
            raise AttributeError('command %s does not have %s parameter' % ('.'.join(self._commands), key))

        return param

    @classmethod
    def __process_bool_param(cls, val, flag, param):
        if param.is_bool_flag and not val:
            if param.secondary_opts:
                flag = param.secondary_opts[0]
                val = True
            else:
                val = None

        return val, flag

    @classmethod
    def __make_list_if_needed(cls, val):
        return val if isinstance(val, (list, tuple)) else [val]

    def __convert_to_arg(self, cmd_args, key, val):
        flag = '--' + key.replace('_', '-')

        param = self.__validate_param(key, flag)

        val, flag = self.__process_bool_param(val, flag, param)

        val = self.__make_arg_list(key, val, param)

        for single_val in val:
            if single_val is None:
                continue

            cmd_args.append(flag)
            if param.is_bool_flag:
                continue

            cmd_args.extend([str(single_val_item) for single_val_item in self.__make_list_if_needed(single_val)])

    def _convert_to_args(self, *args, **kwargs):
        cmd_args = ['--output-format', 'json']

        if self._config_file is not None:
            cmd_args.extend(['--config-file', self._config_file])

        for cmd in self._commands:
            cmd_args.append(str(cmd))

        for val in args:
            cmd_args.append(str(val))

        for key, val in kwargs.items():
            self.__convert_to_arg(cmd_args, key, val)

        return cmd_args

    def _run(self, *args, **kwargs):
        from click.testing import CliRunner

        cmd_args = self._convert_to_args(*args, **kwargs)
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(self._cli, cmd_args, catch_exceptions=False)

        if result.exit_code != 0:
            try:
                exception_text = result.stderr.strip()
            except ValueError:
                exception_text = None

            raise ApiException(exception_text)

        if not result.stdout:
            return

        try:
            return json.loads(result.stdout)
        except ValueError:
            msg = 'command output is not json format:\n"%s"' % result.stdout
            raise InvalidJsonOutput(msg)


class _ApiProxy:
    def __init__(self, cli, *commands, **kwargs):
        self._cli = cli
        self._commands = list(commands) or []
        config_ctx = kwargs.pop('config_ctx', None)
        self._config_ctx = config_ctx or {}

    def _append_command(self, name):
        commands = self._commands[:]
        name = name.replace('_', '-')
        commands.append(name)

        return commands

    def _find_cli(self, name):
        current_cli = self._cli

        for current_cmd in self._append_command(name):
            if current_cmd in current_cli.commands:
                current_cli = current_cli.commands[current_cmd]
                continue

            raise AttributeError('command %s not found' % name)

        return current_cli

    def __getattr__(self, name):
        cli = self._find_cli(name)

        commands = self._append_command(name)
        proxy = _ApiProxy(self._cli, *commands, config_ctx=self._config_ctx)
        if isinstance(cli, click.Group):
            return proxy

        return _ApiCall(self._cli, cli, *commands, **self._config_ctx)


__as_api = None


def as_api(config_file=None):
    global __as_api

    if __as_api is not None:
        return __as_api

    from missinglink.commands.global_cli import cli, add_commands

    add_commands()

    config_ctx = {
        'config_file': config_file
    }

    __as_api = _ApiProxy(cli, config_ctx=config_ctx)

    return __as_api
