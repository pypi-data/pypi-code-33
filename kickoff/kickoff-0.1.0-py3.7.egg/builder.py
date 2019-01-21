import click
import logging
import inspect
from functools import wraps
from .logger import log
from .exceptions import exception_guard
from . inspectutils import get_all_defaults
from . import cmdpath


class CmdGroupsManager:
    """ Manage collection of command groups
    """

    def __init__(self, galaxy, config, app_doc):
        self._galaxy = galaxy
        self._config = config
        top_group = self._create_top_group(app_doc)
        self._groups = {cmdpath.root: top_group}


    def _create_top_group(self, doc):
        def target(): pass
        target.__doc__ = doc
        context_settings = {}

        if self._config.help_option_names is not None:
            context_settings['help_option_names'] = self._config.help_option_names

        group = click.group(context_settings=context_settings)(target)

        if self._config.version_option is not None:
            group = click.version_option(**self._config.version_option)(group)

        return group


    def _create_group(self, name, doc):
        def target(): pass
        target.__doc__ = doc
        return click.group(name=name)(target)


    def _obtain_group(self, path):
        try:
            return self._groups[path]
        except KeyError:
            base_path, name = path
            base_group = self._obtain_group(base_path)
            namespace = self._galaxy[path]
            doc = namespace['__doc__']
            new_group = self._create_group(name, doc)
            base_group.add_command(new_group)
            self._groups[path] = new_group
            return new_group


    def _wrap_command(self, cmd, arg_spec):

        @wraps(cmd)
        def command_wrapper(*args, **kwargs):

            # we assume that click allways passes all the parameters and options in kwargs
            assert args == (), 'internal error'
            kwargs_ = kwargs.copy()

            # put args and varargs in a row
            varargs = kwargs_.pop(arg_spec.varargs, () )
            plain_args = tuple(kwargs_.pop(arg_name) for arg_name in arg_spec.args)
            args_ = (*plain_args, *varargs)

            # execute command with error handling
            with exception_guard(error_handler=self._config.error_handler,
                                usage_error_cls=self._config.usage_error_cls,
                                expected_error_cls=self._config.expected_error_cls):

                ret = cmd(*args_, **kwargs_)

            # report result
            if self._config.result_file is not None:
                if ret is not None:
                    print(ret, file=self._config.result_file)

        return command_wrapper


    def add_command(self, path, func):
        log.debug(f"Registering function {func.__qualname__!r} as {path!r} command")

        arg_spec = inspect.getfullargspec(func)
        all_defaults = get_all_defaults(arg_spec)

        cmd_opts = arg_spec.annotations.get('return', {})
        command_wrapper = self._wrap_command(func, arg_spec)
        cmd = click.command(**cmd_opts)(command_wrapper)

        def update_settings(settings, annotations):
            if isinstance(annotations, dict):
                settings.update(annotations)
            else:
                log.warning(f'Annotation of dict type expected, got {type(annotations).__name__} instead, annotation will be ignored')

        # adding arguments
        for arg in arg_spec.args:
            required = arg not in all_defaults
            default = all_defaults.get(arg)
            log.debug(f'Arg: path={arg!r}, required={required}, default={default!r}')
            settings = dict(required=required, default=default)
            ann = arg_spec.annotations.get(arg, {})
            update_settings(settings, ann)
            cmd = click.argument(arg, **settings)(cmd)

        # adding options
        for opt in arg_spec.kwonlyargs:
            required = opt not in all_defaults
            default = all_defaults.get(opt)
            show_default = opt in all_defaults
            is_flag = isinstance(default, bool)
            settings = dict(required=required, default=default, show_default=show_default, is_flag=is_flag)
            ann = arg_spec.annotations.get(opt, {})
            alias = ann.pop('alias', None)
            log.debug(f'Opt: path={opt!r}, required={required}, default={default!r}, alias={alias!r}')
            if alias is not None:
                assert isinstance(alias, str), 'alias expected to be of str type'
                assert alias.startswith('-'), "alias should start with '-'"
                assert len(alias) == 2, "alias should consist of one character preceded by '-'"
            aliases = filter(None, (alias,) )
            update_settings(settings, ann)
            cmd = click.option(f'--{opt}', *aliases, **settings)(cmd)

        # adding variadic arguments
        if arg_spec.varargs:
            log.debug(f'VarArgs: path={arg_spec.varargs!r}')
            cmd = click.argument(arg_spec.varargs, nargs=-1)(cmd)

        # checking varargs
        if arg_spec.varkw:
            log.warning(f"Kwargs are not supported, ignoring {arg_spec.varkw!r}")

        # adding command to the group
        base_path, name = path
        group = self._obtain_group(base_path)
        group.add_command(cmd)


    def run_top_group(self, app_args, app_name):
        prog_name = self._config.prog_name
        if prog_name is None:
            prog_name=app_name
        self._groups[cmdpath.root](app_args, prog_name=prog_name)

