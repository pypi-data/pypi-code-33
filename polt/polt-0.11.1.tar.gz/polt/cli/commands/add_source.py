# system modules
import logging
import re
import itertools
import importlib
import shlex
import shutil
import sys

# internal modules
import polt
from polt.cli.utils import options_spec, python_class_spec
from polt.cli.commands.main import cli

# external modules
import click

logger = logging.getLogger(__name__)

parser_aliases = polt.extensions.EntryPointExtensions.get(
    polt.version.POLT_PARSER_ENTRY_POINT, aliases=True
)
short_parser_aliases = polt.extensions.EntryPointExtensions.short_aliases(
    parser_aliases
)


def cmd_spec(ctx, param, value):
    if value in ("-", "stdin", None):
        return value
    executable = next(iter(shlex.split(value)), None)
    if shutil.which(executable or ""):
        return value
    else:
        raise click.BadParameter(
            _(
                "could not find executable {executable} "
                "from given command {value}. "
                "If you can execute {executable} from your command-line, "
                "try using the output of `which {executable}` as executable."
            ).format(executable=repr(executable), value=repr(value)),
            param=param,
            ctx=ctx,
        )


@cli.command(help=_("add a new data source"))
@click.option(
    "-p",
    "--parser",
    metavar=_("class").upper(),
    callback=python_class_spec(parser_aliases),
    help=_(
        "parser class to use. "
        "This can be a built-in parser ({native_parsers}) "
        "or a class specification to a subclass of Parser "
        "(like 'mypackage.MyParser')"
    ).format(
        native_parsers=polt.l10n.join(
            short_parser_aliases, last_sep=" {} ".format(_("or"))
        )
    ),
)
@click.option(
    "-c",
    "--cmd",
    metavar=_("command").upper(),
    callback=cmd_spec,
    help=_(
        "the command to use as source for the parser. "
        "The default is to use data from stdin."
    ),
)
@click.option(
    "-e",
    "--encoding",
    metavar=_("encoding").upper(),
    help=_(
        "the encoding to use to decode the data. "
        "The default is no encoding which means to pass raw bytes to "
        "the parser."
    ),
)
@click.option(
    "-o",
    "--option",
    "parser_options",
    metavar="{option}={value}".format(
        option=_("option"), value=_("value")
    ).upper(),
    multiple=True,
    callback=options_spec,
    help=_(
        "further options for the parser. "
        "Multiple specifications of this option are possible. "
        "The parser's attribute (previously snake-cased) {option} "
        "will be set to the string {value}. If {value} is not given, {option} "
        "is set to {value_default}."
    ).format(
        option=_("option").upper(),
        value=_("value").upper(),
        value_default=repr(polt.utils.to_float(True)),
    ),
)
@click.option(
    "--max-rate",
    metavar=_("Hertz").upper(),
    help=_(
        "Maximum data rate (datasets per second in Hertz) "
        "to append to the shared buffer. Default is unlimited. "
        "Use this to if the input stream is too fast to plot."
        "Note that the effective data rate will be lower than this."
    ),
    type=click.FloatRange(min=sys.float_info.min),
)
@click.option(
    "--flush-after",
    metavar=_("seconds"),
    help=_(
        "How many seconds to buffer recieved datasets in the streamers "
        "before appending them to the shared buffer. The default is 0 which "
        "means to flush recieved data right away. Increasing this value "
        "can help if the input data arrives too fast for the plot to catch up."
    ),
    type=click.FloatRange(min=0, clamp=True),
)
@click.pass_context
def add_source(
    ctx, parser, cmd, parser_options, encoding, max_rate, flush_after
):
    if not (parser or cmd):
        raise click.UsageError(
            _("Specify at least either --parser or --cmd"), ctx=ctx
        )
    if parser is None:
        parser = polt.parser.numberparser.NumberParser
        parser = ".".join((parser.__module__, parser.__name__))
    if cmd is None:
        cmd = "-"
    config = ctx.obj["config"]
    matching_sections = list(config.matching_source_section(command=cmd))
    for section in matching_sections:
        logger.warning(
            _(
                "Removing previously existing configuration section {section} "
                "because it matches the given command-line source command "
                "{clicmd}."
            ).format(
                clicmd=repr(cmd),
                section=_("{section} (parsing {cmd} with {parser})").format(
                    section=repr(section.name),
                    parser=section.get("parser"),
                    cmd=repr(section.get("command")),
                ),
            )
        )
        config.remove_section(section.name)
    # determine a nice section name
    section_name = "{}:{}".format(
        config.SOURCE_SECTION_PREFIX,
        parser_options.get(
            "name", "stdin" if cmd == "-" else polt.utils.normalize_cmd(cmd)
        ),
    )
    config.add_section(section_name)
    config.update_option(section_name, "command", cmd)
    config.update_option(section_name, "parser", parser)
    config.update_option(section_name, "encoding", encoding)
    for option, value in parser_options.items():
        config[section_name]["parser.{}".format(option)] = value
    streamer_options = {"max-rate": max_rate, "flush-after": flush_after}
    for option, value in streamer_options.items():
        if value is not None:
            config[section_name]["streamer.{}".format(option)] = str(value)
