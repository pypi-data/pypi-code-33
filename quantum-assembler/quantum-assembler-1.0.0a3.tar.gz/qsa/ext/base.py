import copy
import logging
import os

import jinja2

from qsa.cli.exc import CommandError
####################MOVE
import os

import yaml

LF = '\n'
WS = ' '


def format_environment_variable(value, inline=True):
    symbol = value if os.getenv('QSA_PREFIX_ENVIRONMENT') != '1'\
        else '{QSA_PKG_NAME}_{value}'.format(value=value, **os.environ).upper()
    return f'${symbol}' if inline else symbol


def envdefault(key, value):
    key = format_environment_variable(key, inline=False)
    return f'${{{key}-{value}}}'


def dictsort(d):
    return sorted(d.items(), key=lambda x: x[0])


def limit(value, max_length, indent, prefix=''):
    """Limits the length of each line in the output to
    `length`, indented by `indent`, broken up on word
    boundaries.
    """
    INDENT = WS * indent
    NEWLINE = LF + INDENT
    words = value.split(WS)
    stmt = ''
    if prefix:
        stmt = f'{prefix} '
    result = ''
    for word in words:
        if not word: # Value container consecutive spaces.
            continue
        length = len(stmt[stmt.rfind('\n'):])\
            if stmt.rfind('\n') != -1\
            else len(stmt)
        if (length + len(word) > max_length):
            stmt = str.strip(stmt, WS)
            stmt += NEWLINE + ('' if not prefix else f'{prefix} ')
        stmt += f'{word} '
    return str.strip(stmt)

def render_yaml(value):
    if hasattr(value, 'as_dict'):
        value = value.as_dict()
    return yaml.safe_dump(value, default_flow_style=False, indent=2)\
        .strip().rstrip('.').strip()

####################MOVE


class BaseExtension:
    logger = logging.getLogger('qsa')

    #: The name of the extension. This attribute is required.
    name = None

    #: Specifies the command name. If this attribute is ``None``, the
    #: extension is assumed not to implement a subcommand.
    command_name = None

    #: Configures subcommands for the parser.
    subcommands = []

    #: Help text to be displayed when ``qsa <command_name> --help`` is invoked.
    help_text = None

    #: Specifies the schema class to load and dump the configuration.
    #: If :attr:`BaseExtension.schema_class` is ``None``, it is
    #: assumed that the extension does not have a configuration.
    schema_class = None

    #: Defines the order of extension execution.
    weight = 0.0

    # Specifies arguments for the template environment.
    template_params = {
        'lstrip_blocks': False,
        'trim_blocks': False
    }

    def __init__(self, config, assembler, injector):
        self.config = config
        self.assembler = assembler
        self.injector = injector
        self.spec = None
        self.quantum = None
        self.template = jinja2.Environment(
            loader=jinja2.ChoiceLoader([
                jinja2.PackageLoader(self.__module__, 'templates'),
                jinja2.PackageLoader('qsa', 'templates')
            ]),
            **self.template_params
        )
        self.template.globals.update(envname=format_environment_variable)
        self.template.globals.update(envdefault=envdefault)
        self.template.filters.update({
            'yaml': render_yaml,
            'dictsort': dictsort,
            'limit': limit
        })

    def on_spec_loading(self, data, quantum):
        """Invoked when the content of :attr:`~qsa.const.QUANTUMFILE` is
        deserialized into a dictionary.

        Args:
            data: the data as loaded from the Quantum specification.
            quantum: the parsed and cleaned data. Note that this is the
                full specification, not only for this extension.
        """
        assert not self.spec
        if not self.schema_class:
            self.logger.debug("Extension %s does not implement configuration.",
                self.name)
            return
        schema = self.schema_class.getforload()
        try:
            self.spec = schema.load(copy.deepcopy(data))
        except Exception as e:
            self.spec = {}
        quantum.update(copy.deepcopy(self.spec))

    def on_spec_loaded(self, quantum):
        """Invoked when the full Quantum specification is loaded."""
        assert not self.quantum
        self.quantum = quantum

    def on_spec_updated(self, quantum):
        """Invoked when the Quantum specification is updated."""
        if not self.schema:
            return
        self.spec = quantum.loadspec(self.schema_class)

    def on_spec_render(self, qf):
        """Invoked when the Quantumfile is being rendered to string."""
        if not self.schema_class:
            return
        qf.addsection(self.name, self.render('Quantumfile.j2'),
            self.weight)

    def on_spec_section_render(self, qf, section, subsections):
        """Invoked when a specific section is rendered."""
        pass

    def _createcommand(self, subcommands):
        if self.command_name is None:
            return
        parser = self.createcommand(subcommands)
        self._add_parser_defaults(parser)
        if self.subcommands:
            parent = parser.add_subparsers(dest='command')
        for subcommand in self.subcommands:
            self._createsubcommand(parent, **subcommand)

    def _createsubcommand(self, parent, name, args):
        parser = parent.add_parser(name)
        for arg in args:
            parser.add_argument(**arg)
        parser.set_defaults(func=self.run_subcommand)

    def _add_parser_defaults(self, parser):
        parser.set_defaults(workdir=os.getenv('QSA_WORKDIR'))
        parser.set_defaults(func=self.handle)

    def createcommand(self, parent):
        """Exposes a subcommand to the ``qsa`` command-line
        interface.
        """
        parser = parent.add_parser(self.command_name,
            help=self.help_text)
        return parser

    def run_subcommand(self, args):
        f = getattr(self, f'handle_{args.command.replace("-", "_")}')
        self.injector.call(f)

    def handle(self):
        self.logger.warning('%s.Extension.handle() is not implemented',
            self.__module__)

    def render(self, template_name, ctx=None):
        """Renders the Jinja2 template `template_name` using the given
        context `ctx`.
        """
        ctx = ctx or {}
        ctx.update({
            'IS_QUANTUM_INIT': os.getenv('QSA_INIT') == '1'
        })
        t = self.template.get_template(template_name)
        return t.render(spec=copy.deepcopy(self.spec),
            quantum=dict(self.quantum), **ctx)

    def fail(self, msg):
        raise CommandError(msg)

    def setup_injector(self, injector):
        """Hook to allow extensions to setup the dependency
        injector.
        """
        pass
