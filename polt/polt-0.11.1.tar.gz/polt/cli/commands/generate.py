# system modules
import logging
import itertools
import functools
import collections
import time
import sys
import csv
import random
import re
import math

# internal modules
import polt
from polt.cli.commands.main import cli

# external modules
import click

logger = logging.getLogger(__name__)

column_spec_regex = re.compile(
    r"(?:([^=(]*?)\s*=?\s*)?"  # name
    r"(?:"
    r"([^=(]+)"  # function
    r"(?:\s*\(\s*([^)]*)\s*\))?"  # options
    r")?"
)


def matching_random_function(spec, *args, **kwargs):
    """
    Generator yielding the next matching random number generating method of the
    :class:`random.Random` class. A method is considered a matching random
    number generator if its name contains the given specification, it returns a
    single :class:`float` and produces different values when called multiple
    times.

    Args:
        spec (str): the function specification string
        args, kwargs: further arguments to hand to the function

    Yields:
        callable : the matching random number generator wrapped with
            :func:`functools.partial` callable without arguments
    """
    for attr in filter(lambda x: spec in x, reversed(dir(random.Random))):
        obj = getattr(random, attr, None)
        if not hasattr(obj, "__call__"):
            continue
        func = functools.partial(obj, *args, **kwargs)
        try:
            assert isinstance(func(), float), "not float return value"
            assert len(set(func() for i in range(10))) == 10, "not random"
        except BaseException as e:
            continue
        yield func


def column_spec(ctx, param, value):
    m = column_spec_regex.fullmatch(value.strip())
    if not m:
        raise click.BadParameter(
            _("Specify a column like {examples}, not like {given}").format(
                examples=polt.l10n.join(
                    map(
                        repr,
                        map(
                            str.upper,
                            itertools.accumulate(
                                (
                                    _("name"),
                                    "=" + _("function"),
                                    "({})".format(_("options")),
                                )
                            ),
                        ),
                    ),
                    last_sep=" {} ".format(_("or")),
                ),
                given=repr(value),
            ),
            param=param,
            ctx=ctx,
        )
    col, func_spec, args_spec = m.groups()
    col = col if col else ("column" if func_spec is None else func_spec)
    args = tuple(
        map(
            functools.partial(polt.utils.to_float, default_on_failure=False),
            map(str.strip, args_spec.split(",")),
        )
        if args_spec
        else tuple()
    )
    default_funcs = {
        "sin": lambda: math.sin(
            time.time() * (args[0] if args else 1) * 2 * math.pi
        ),
        "cos": lambda: math.cos(
            time.time() * (args[0] if args else 1) * 2 * math.pi
        ),
        "time": time.time,
        "row": itertools.count(1).__next__,
        "walk": itertools.accumulate(
            random.uniform(-0.5, 0.5) for i in itertools.count()
        ).__next__,
    }
    if func_spec:
        func = default_funcs.get(func_spec)
        if not func:
            func = next(matching_random_function(func_spec, *args), None)
            if not func:
                raise click.BadParameter(
                    _(
                        "No random number generating method of random.Random "
                        "found having {spec} in its name and "
                        "taking {n_args} arguments {args}"
                    ).format(
                        spec=repr(func_spec),
                        n_args=len(args),
                        args="({})".format(
                            polt.l10n.join(
                                map(repr, args),
                                last_sep=" {} ".format(_("and")),
                            )
                        )
                        if args
                        else "",
                    ),
                    param=param,
                    ctx=ctx,
                )
    else:
        func = default_funcs.get(col, random.random)
    return (col, func)


@cli.command(
    help="\n\n".join(
        (
            _("generate random CSV data"),
            _("This command can be used to generate random CSV output."),
        )
    ),
    short_help=_("generate random CSV data"),
)
@click.option(
    "-o",
    "--output",
    metavar=_("file").upper(),
    help=_("File to write to. Defaults to standard output."),
    default=sys.stdout,
    type=click.File(mode="w"),
)
@click.option(
    "-c",
    "--column",
    "columns",
    metavar="[{}=]{}[({})]".format(
        _("name"), _("function"), _("options")
    ).upper(),
    help=_(
        "Add a column named {name_part} (or {func_part} unless specified). "
        "{func_part} may be (part of) the name "
        "of a random number generation method of the random.Random class "
        "(see https://docs.python.org/3/library/random.html) optionally "
        "taking the options {options_part} (comma-separated list of values). "
        "Specifying 'time' for {func_part} "
        "adds a column containing the current time as floating-point epoch "
        "timestamp. Equally, 'row' may be used to add a column containing "
        "the index of the current row. 'walk' generates a random walk. "
        "'sin(Hz)' or 'cos(Hz)' can be used to create waves. "
        "The default {func_part} is a uniform "
        "distribution in the interval [0, 1)."
    ).format(
        name_part=_("name").upper(),
        func_part=_("function").upper(),
        options_part=_("options").upper(),
    ),
    multiple=True,
    callback=lambda c, p, v: collections.OrderedDict(
        map(functools.partial(column_spec, c, p), v)
    ),
)
@click.option(
    "--header/--no-header",
    "output_header",
    help=_("Whether to output the header"),
    default=True,
    is_flag=True,
)
@click.option(
    "-d",
    "--delimiter",
    metavar=_("character").upper(),
    help=_("The delimiter to use. The default is a comma (,)."),
    default=",",
)
@click.option(
    "-r",
    "--max-rate",
    metavar=_("Hertz").upper(),
    help=_("Limit the data output rate (rows per second)"),
    default=float("inf"),
    type=click.FloatRange(min=sys.float_info.min),
)
@click.option(
    "-n",
    "--rows",
    metavar=_("amount").upper(),
    help=_("Limit the number of output data rows"),
    type=click.IntRange(min=0),
)
@click.option(
    "--stop-after",
    metavar=_("seconds").upper(),
    help=_("Stop outputting data after a given amount of seconds."),
    default=float("inf"),
    type=click.FloatRange(min=sys.float_info.min),
)
@click.option(
    "-s",
    "--seed",
    metavar=_("integer").upper(),
    help=_("Seed to use"),
    default=float("inf"),
    type=click.FLOAT,
)
@click.option(
    "-p",
    "--precision",
    metavar=_("integer"),
    help=_("How many precision digits to diplay for all columns"),
    type=click.IntRange(min=0),
)
def generate(
    columns,
    output,
    output_header,
    delimiter,
    max_rate,
    stop_after,
    rows,
    seed,
    precision,
):
    random.seed(seed)
    columns = columns or collections.OrderedDict((("random", random.random),))
    start_time = time.time()
    min_tdiff = 1 / max_rate
    last_output_time = float("-inf")
    writer = csv.DictWriter(
        output, fieldnames=columns.keys(), delimiter=delimiter
    )
    if output_header:
        writer.writeheader()
    formatter = (
        str if precision is None else "{{:.{}f}}".format(precision).format
    )
    for i in itertools.count() if rows is None else range(rows):
        if time.time() > start_time + stop_after:
            break
        if time.time() - last_output_time < min_tdiff:
            continue
        writer.writerow(
            {col: formatter(func()) for col, func in columns.items()}
        )
        output.flush()
        last_output_time = time.time()
