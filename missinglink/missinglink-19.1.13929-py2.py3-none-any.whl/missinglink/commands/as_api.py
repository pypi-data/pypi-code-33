# -*- coding: utf8 -*-
import json
import click


class ApiException(Exception):
    pass


class _ApiCall:
    def __init__(self, cli, *commands, **kwargs):
        self._cli = cli
        self._commands = commands
        config_file = kwargs.pop('config_file', None)
        self._config_file = config_file

    def __call__(self, *args, **kwargs):
        return self._run(*args, **kwargs)

    def _convert_to_args(self, *args, **kwargs):
        cmd_args = ['--output-format', 'json']

        if self._config_file is not None:
            cmd_args.extend(['--config-file', self._config_file])

        for cmd in self._commands:
            cmd_args.append(str(cmd))

        for val in args:
            cmd_args.append(str(val))

        for key, val in kwargs.items():
            key = key.replace('_', '-')
            cmd_args.append('--' + key)
            cmd_args.append(str(val))

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

        return json.loads(result.stdout)


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

        return _ApiCall(self._cli, *commands, **self._config_ctx)


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
