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

filter_aliases = polt.extensions.EntryPointExtensions.get(
    polt.version.POLT_FILTER_ENTRY_POINT, aliases=True
)
short_filter_aliases = polt.extensions.EntryPointExtensions.short_aliases(
    filter_aliases
)


@cli.command(help=_("add a new data filter"))
@click.option(
    "-f",
    "--filter",
    "filter_spec",
    metavar=_("class").upper(),
    callback=python_class_spec(filter_aliases),
    required=True,
    help=_(
        "filter class to use. "
        "This can be a built-in filter ({native_filters}) "
        "or a class specification to a subclass of Filter "
        "(like 'mypackage.MyFilter')"
    ).format(
        native_filters=polt.l10n.join(
            short_filter_aliases, last_sep=" {} ".format(_("or"))
        )
    ),
)
@click.option(
    "-o",
    "--option",
    "filter_options",
    metavar="{option}={value}".format(
        option=_("option"), value=_("value")
    ).upper(),
    multiple=True,
    callback=options_spec,
    help=_(
        "further options for the filter. "
        "Multiple specifications of this option are possible. "
        "The filter's attribute (previously snake-cased) {option} "
        "will be set to the string {value}. If {value} is not given, {option} "
        "is set to {value_default}."
    ).format(
        option=_("option").upper(),
        value=_("value").upper(),
        value_default=repr(polt.utils.to_float(True)),
    ),
)
@click.pass_context
def add_filter(ctx, filter_spec, filter_options):
    config = ctx.obj["config"]
    section_name = config.add_section(
        "{}:{}".format(config.FILTER_SECTION_PREFIX, filter_spec)
    )
    config.update_option(section_name, "filter", filter_spec)
    for option, value in filter_options.items():
        config[section_name]["filter.{}".format(option)] = value
