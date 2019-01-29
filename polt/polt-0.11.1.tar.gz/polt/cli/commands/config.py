# system modules
import io
import logging

# internal modules
import polt
from polt.config import DEFAULT_CONFIG_FILES
from polt.cli.commands.main import cli

# external modules
import click

logger = logging.getLogger(__name__)


@cli.command(
    help="\n\n".join(
        (
            _("managing configuration"),
            _(
                "The configuration files {files} are read by default "
                "if they exist "
                "unless the top-level --no-config option was specified."
            ).format(files=polt.l10n.join(map(repr, DEFAULT_CONFIG_FILES))),
            _(
                "Without options, this command just dumps the current "
                "configuration."
            ),
        )
    ),
    short_help=_("managing configuration"),
)
@click.option(
    "-r",
    "--read",
    help=_("read a configuration file"),
    metavar=_("file").upper(),
    type=click.File("r"),
)
@click.option(
    "-s",
    "--save",
    help=_("save the current configuration to file"),
    metavar=_("file").upper(),
    type=click.File("w"),
)
@click.pass_context
def config(ctx, read, save):
    if read:
        logger.info(
            _("reading configuration file {file}").format(file=repr(read.name))
        )
        ctx.obj["config"].read_file(read)
    if save:
        logger.info(
            _("saving current configuration to file {file}").format(
                file=repr(save.name)
            )
        )
        ctx.obj["config"].write(save)
    if not (read or save):
        buf = io.StringIO()
        ctx.obj["config"].write(buf)
        click.echo(buf.getvalue().strip())
