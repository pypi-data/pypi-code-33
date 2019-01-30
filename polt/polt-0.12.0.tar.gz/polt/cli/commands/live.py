# system modules
import logging
import importlib
import subprocess
import shlex
import multiprocessing
import sys
import io

# internal modules
import polt
from polt.cli.utils import options_spec, python_class_spec
from polt.cli.commands.main import cli

# external modules
import click

logger = logging.getLogger(__name__)

animator_aliases = polt.extensions.EntryPointExtensions.get(
    polt.version.POLT_ANIMATOR_ENTRY_POINT, aliases=True
)
short_animator_aliases = polt.extensions.EntryPointExtensions.short_aliases(
    animator_aliases
)


@cli.command(
    help="\n\n".join(
        (
            _("plot live data"),
            _(
                "This command parses the current configuration, "
                "sets up all parsers with their respective sources "
                "and launches the interactive plot window."
            ),
            _(
                "The animation can be paused and resumed "
                "by hitting the spacebar."
            ),
        )
    ),
    short_help=_("plot live data"),
)
@click.option(
    "--soft-shutdown/--hard-shutdown",
    "soft_shutdown",
    help=_("Shut down input threads gracefully"),
    default=None,
    is_flag=True,
)
@click.option(
    "-n",
    "--no-plot",
    help=_("Don't actually do any live plotting, just set the configuration"),
    default=False,
    is_flag=True,
)
@click.option(
    "-a",
    "--animator",
    "animator_spec",
    metavar=_("animator").upper(),
    help=_(
        "animator class to use. "
        "This can be a built-in animator ({native_animators}) "
        "or a class specification to a subclass of Animator "
        "(like 'mypackage.MyAnimator')"
    ).format(
        native_animators=polt.l10n.join(
            short_animator_aliases, last_sep=" {} ".format(_("or"))
        )
    ),
    default="lines",
    callback=python_class_spec(animator_aliases),
)
@click.option(
    "-o",
    "--option",
    "animator_options",
    metavar="{option}={value}".format(
        option=_("option"), value=_("value")
    ).upper(),
    multiple=True,
    callback=options_spec,
    help=_(
        "further options for the animator. "
        "Multiple specifications of this option are possible. "
        "The animator's attribute (previously snake-cased) {option} "
        "will be set to the string {value}. If {value} is not given, {option} "
        "is set to {value_default}."
    ).format(
        option=_("option").upper(),
        value=_("value").upper(),
        value_default=repr(polt.utils.to_float(True)),
    ),
)
@click.pass_context
def live(ctx, soft_shutdown, no_plot, animator_spec, animator_options):
    config = ctx.obj["config"]
    config.update_option("plot", "soft-shutdown", soft_shutdown)
    config.update_option("plot", "animator", animator_spec)
    for option, value in animator_options.items():
        config.update_option("plot", "animator.{}".format(option), value)

    if no_plot:
        logger.info(_("Skip plotting as requested via command-line"))
        return

    try:
        streamers = list(config.streamer)
    except polt.config.SourceSectionError as e:
        raise click.ClickException(
            _(
                "Problem creating streamer "
                "with parser from configuration: {err}"
            ).format(err=e)
        )

    if not streamers:
        logger.info(
            " ".join(
                [
                    _("No sources specified."),
                    _("Falling back to reading numbers from stdin."),
                ]
            )
        )
        if sys.stdin.isatty():
            click.echo(
                _(
                    "You may now repeatedly type any numbers "
                    "and press <Enter>."
                )
            )
        streamers = [
            polt.streamer.Streamer(
                parser=polt.parser.numberparser.NumberParser(sys.stdin)
            )
        ]

    # load filters
    try:
        filters = list(config.filter)
    except polt.config.FilterSectionError as e:
        raise click.ClickException(
            _("Could not load filters from configuration: {err}").format(err=e)
        )

    # load animator
    try:
        animator = config.animator
    except polt.config.PlotSectionError as e:
        raise click.ClickException(
            _("Could not load animator from configuration: {err}").format(
                err=e
            )
        )

    # set filters on animator
    animator.filters = filters

    with multiprocessing.Manager() as manager:

        def animate_process(buf):
            logger.debug(_("Creating Animator"))
            # connect animator to buffer
            animator.buffer = buf
            logger.debug(_("Running Animator"))
            animator.run()
            logger.debug(_("Animator is done"))

        # create shared buffer
        buf = manager.list()
        # connect streamer to buffers
        for streamer in streamers:
            streamer.buffer = buf
        p = multiprocessing.Process(
            target=animate_process,
            daemon=True,
            kwargs={"buf": buf},
            name=_("PlotProcess"),
        )
        try:
            logger.debug(_("Starting plot process"))
            p.start()
            logger.debug(_("plot process started"))
            logger.debug(_("starting parsing threads"))
            for streamer in streamers:
                logger.debug(
                    _("starting parsing thread {}").format(streamer.name)
                )
                streamer.start()
            logger.debug(_("parsing threads started"))
            p.join()
            logger.debug(_("Plot process exited"))
        except KeyboardInterrupt:
            logger.info(_("User wants to stop"))
        if config.getboolean("plot", "soft-shutdown", fallback=False):
            logger.info(_("shutting down gracefully"))
            try:
                for streamer in streamers:
                    streamer.stop()
                    logger.debug(
                        _("Waiting for thread {} to close").format(
                            streamer.name
                        )
                    )
                    streamer.join()
            except KeyboardInterrupt:
                logger.info(_("Okay, okay, stopping now..."))

    logger.debug(_("live plotting done"))
