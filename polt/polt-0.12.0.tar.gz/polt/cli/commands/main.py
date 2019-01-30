# system modules
import logging

# internal modules
from polt.config import DEFAULT_CONFIG_FILES
import polt.config

# external modules
import click

logger = logging.getLogger(__name__)


@click.group(
    help="\n\n".join(
        (
            "{} - {}".format(
                _("polt").title(), _("Live Data Visualisation via Matplotlib")
            ),
            _(
                "Commands can be chained and will "
                "be executed in the specified order."
            ),
            _(
                "Further information for each command can be viewed "
                "by passing --help to it (e.g. polt live --help)."
            ),
        )
    ),
    context_settings={"help_option_names": ["-h", "--help"]},
    chain=True,
)
@click.option("-q", "--quiet", help=_("only show warnings"), is_flag=True)
@click.option("-v", "--verbose", help=_("verbose output"), is_flag=True)
@click.option(
    "--no-config",
    help=_("don't load any default configuration files"),
    is_flag=True,
)
@click.version_option(help=_("show version and exit"))
@click.pass_context
def cli(ctx, quiet, verbose, no_config):
    # set up logging
    loglevel = logging.DEBUG if verbose else logging.INFO
    loglevel = logging.WARNING if quiet else loglevel
    logging.basicConfig(
        level=loglevel, format="[%(asctime)s] - %(levelname)-8s - %(message)s"
    )
    for n, l in logger.manager.loggerDict.items():
        if not n.startswith("polt"):
            l.propagate = False
    ctx.ensure_object(dict)
    ctx.obj["config"] = polt.config.Configuration()
    if no_config:
        logger.debug(_("skip reading default configuration files"))
    else:
        logger.debug(
            _("read default configuration files {files}").format(
                files=", ".join(map(repr, DEFAULT_CONFIG_FILES))
            )
        )
        ctx.obj["config"].read(DEFAULT_CONFIG_FILES)
