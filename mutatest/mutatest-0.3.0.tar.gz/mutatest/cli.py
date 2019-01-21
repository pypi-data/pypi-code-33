"""Command line interface.
"""
import argparse
import logging
import random
import shlex
import sys

from datetime import timedelta
from pathlib import Path
from textwrap import dedent
from typing import NamedTuple, Optional

from setuptools import find_packages  # type:ignore

import mutatest

from mutatest.cache import check_cache_invalidation_mode
from mutatest.controller import clean_trial, run_mutation_trials
from mutatest.report import analyze_mutant_trials, write_report
from mutatest.transformers import get_compatible_operation_sets


LOGGER = logging.getLogger(__name__)
FORMAT = "%(asctime)s: %(message)s"
DEBUG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class RunMode(NamedTuple):
    """Running mode choices."""

    mode: str

    @property
    def break_on_detection(self) -> bool:
        return self.mode in ["d", "sd"]

    @property
    def break_on_survival(self) -> bool:
        return self.mode in ["s", "sd"]

    @property
    def break_on_error(self) -> bool:
        # Set to TRUE for the cli as a default, may add CLI control options later
        return True

    @property
    def break_on_unknown(self) -> bool:
        # Set to TRUE for the cli as a default, may add CLI control options later
        return True


class TrialTimes(NamedTuple):
    """Container for trial run times used in summary report."""

    clean_trial_1: timedelta
    clean_trial_2: timedelta
    mutation_trials: timedelta


class PositiveIntegerAction(argparse.Action):
    """Custom action for ensuring positive integers in number of trials."""

    def __call__(self, parser, namespace, values, option_string=None):  # type: ignore
        if values <= 0:
            parser.error("{0} must be a non-zero positive integer.".format(option_string))

        setattr(namespace, self.dest, values)


def cli_epilog() -> str:

    main_epilog = dedent(
        """
    Additional command argument information:
    ========================================

    Exclude:
    --------
     - Useful for excluding files that are not included in test coverage. Use a space delimited
       list in a string for the files e.g. "__init__.py ignore.py also_ignore.py".

    Mode:
    ------
     - f: full mode, run all possible combinations (slowest but most thorough).
     - s: break on first SURVIVOR per mutated location e.g. if there is a single surviving mutation
          at a location move to the next location without further testing.
          This is the default mode.
     - d: break on the first DETECTION per mutated location e.g. if there is a detected mutation on
          at a location move to the next one.
     - sd: break on the first SURVIVOR or DETECTION (fastest, and least thorough).

     The API for mutatest.controller.run_mutation_trials offers finer control over the
     run method beyond the CLI.

    Output:
    -------
     - You can specify a file name or a full path. The folders in the path will be created if they
       do not already exist. The output is a text file formatted in RST headings.

    Src:
    ----
     - This can be a file or a directory. If it is a directory it is recursively searched for .py
       files. Note that the __pycache__ file associated with the file (or sub-files in a directory)
       will be manipulated during mutation testing. If this argument is unspecified, mutatest will
       attempt to find Python packages (using setuptools.find_packages) and use the first
       entry from that auto-detection attempt.

    Testcmds:
    ---------
     - Specify custom test commands as a string e.g. 'pytest -m "not slow"' for running only
       the test suite without the marked "slow" tests. Shlex.split() is used to parse the
       entered command string. Mutant status e.g. SURVIVED vs. DETECTED is based on the
       return code of the command. Return code 0 = SURVIVED, 1 = DETECTED, 2 = ERROR, and
       all others are UNKNOWN. Stdout is shown from the command if --debug mode is enabled.
    """
    )

    header = "Supported mutation sets"
    description = "These are the current operations that are mutated as compatible sets."
    mutation_epilog = [header, "=" * len(header), description, "\n"]
    for mutop in get_compatible_operation_sets():
        mutation_epilog.extend([mutop.name, "-" * len(mutop.name), f" - {str(mutop.operations)}\n"])

    meta_info = dedent(
        """
    Mutatest information
    ====================
     - Version: {version}
     - License: {license}
     - URL: {url}
     - {copyright}
    """
    ).format_map(
        {
            "version": mutatest.__version__,
            "license": mutatest.__license__,
            "url": mutatest.__uri__,
            "copyright": mutatest.__copyright__,
        }
    )

    return "\n".join([main_epilog] + mutation_epilog + [meta_info])


def cli_args() -> argparse.Namespace:
    """Command line arguments.

    Returns:
        parsed args from ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="Mutatest",
        description=(
            "Python mutation testing. " "Mutatest will manipulate local __pycache__ files."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=cli_epilog(),
    )
    parser.add_argument(
        "-e",
        "--exclude",
        type=lambda x: x.split(),
        default="__init__.py",
        metavar="STR_LIST",
        help="Space delimited string list of .py file names to exclude. (default: '__init__.py')",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["f", "s", "d", "sd"],
        default="s",
        type=str,  # can't lambda format this to RunMode because of choices
        help=("Running modes, see the choice option descriptions below. " "(default: s)"),
    )
    parser.add_argument(
        "-n",
        "--nlocations",
        type=int,
        action=PositiveIntegerAction,
        default=10,
        metavar="INT",
        help=(
            "Number of locations in code to randomly select for mutation from possible targets. "
            "(default: 10)"
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=lambda x: Path(x),
        metavar="PATH",
        default="mutation_report.rst",
        help="Output file location for results. (default: mutation_report.rst)",
    )
    parser.add_argument(
        "-r",
        "--rseed",
        type=int,
        action=PositiveIntegerAction,
        metavar="INT",
        help=("Random seed to use for sample selection."),
    )
    parser.add_argument(
        "-s",
        "--src",
        required=False,
        type=lambda x: Path(x),
        metavar="PATH",
        help=(
            "Source code (file or directory) for mutation testing. "
            "(default: auto-detection attempt)."
        ),
    )
    parser.add_argument(
        "-t",
        "--testcmds",
        required=False,
        default="pytest",
        metavar="STR_CMDS",
        # shelx.split will appropriately handle embedded quotes etc. for tokenization.
        type=lambda x: shlex.split(x),
        help="Test command string to execute. (default: 'pytest')",
    )
    parser.add_argument("--debug", action="store_true", help="Turn on DEBUG level logging output.")

    return parser.parse_args()


def cli_summary_report(
    src_loc: Path,
    args: argparse.Namespace,
    locs_mutated: int,
    locs_identified: int,
    runtimes: TrialTimes,
) -> str:
    """Create a command line summary header for the final reporting.

    Args:
        src_loc: source location
        args: argparse namespace from cli

    Returns:
        str
    """

    cli_summary_template = dedent(
        """\
    Mutatest diagnostic summary
    ===========================
     - Source location: {src_loc}
     - Test commands: {testcmds}
     - Mode: {mode}
     - Excluded files: {exclude}
     - N locations input: {n_locs}
     - Random seed: {seed}

    Random sample details
    ---------------------
     - Total locations mutated: {locs_mutated}
     - Total locations identified: {locs_identified}
     - Location sample coverage: {coverage} %


    Running time details
    --------------------
     - Clean trial 1 run time: {ct1}
     - Clean trial 2 run time: {ct2}
     - Mutation trials total run time: {mt}
    """
    )

    coverage = (locs_mutated / locs_identified) * 100

    fmt_map = {
        "src_loc": str(src_loc.resolve()),
        "testcmds": args.testcmds,
        "mode": args.mode,
        "exclude": args.exclude,
        "n_locs": args.nlocations,
        "seed": args.rseed,
        "locs_mutated": locs_mutated,
        "locs_identified": locs_identified,
        "coverage": f"{coverage:.2f}",
        "ct1": runtimes.clean_trial_1,
        "ct2": runtimes.clean_trial_2,
        "mt": runtimes.mutation_trials,
    }

    return cli_summary_template.format_map(fmt_map)


def cli_main() -> None:
    """Entry point to run CLI args and execute main function."""
    # Run a quick check at the beginning in case of later OS errors.
    check_cache_invalidation_mode()
    args = cli_args()
    main(args)


def get_src_location(src_loc: Optional[Path] = None) -> Path:
    """Find packages if the src_loc is not set

    Args:
        src_loc: current source location, defaults to None

    Returns:
        Path to the source location

    Raises:
        FileNoeFoundError if the source location doesn't exist.
    """
    if not src_loc:
        find_pkgs = find_packages()
        if find_pkgs:
            src_loc = Path(find_pkgs[0])
            return src_loc
    else:
        if src_loc.exists():
            return src_loc

    raise FileNotFoundError(
        "No source directory specified or automatically detected. "
        "Use --src or --help to see options."
    )


def main(args: argparse.Namespace) -> None:

    src_loc = get_src_location(args.src)

    # set the logging level based on the debug flag in args
    # when in debug mode the test stdout is not captured by subprocess.run
    logging.basicConfig(
        format=DEBUG_FORMAT if args.debug else FORMAT,
        level=logging.DEBUG if args.debug else logging.INFO,
        stream=sys.stdout,
    )

    # Run the pipeline with no mutations first to ensure later results are meaningful
    clean_runtime_1 = clean_trial(src_loc=src_loc, test_cmds=args.testcmds)

    # Run the mutation trials based on the input argument
    run_mode = RunMode(args.mode)

    if args.rseed:
        LOGGER.info("Random seed set by user to: %s.", args.rseed)
        random.seed(a=args.rseed)

    results_summary = run_mutation_trials(
        src_loc=src_loc,
        test_cmds=args.testcmds,
        exclude_files=args.exclude,
        n_locations=args.nlocations,
        break_on_detected=run_mode.break_on_detection,
        break_on_survival=run_mode.break_on_survival,
        break_on_error=run_mode.break_on_error,
        break_on_unknown=run_mode.break_on_unknown,
    )

    # Run the pipeline with no mutations last to ensure cleared cache
    clean_runtime_2 = clean_trial(src_loc=src_loc, test_cmds=args.testcmds)

    runtimes = TrialTimes(
        clean_trial_1=clean_runtime_1,
        clean_trial_2=clean_runtime_2,
        mutation_trials=results_summary.total_runtime,
    )

    # create the report of results
    cli_report = cli_summary_report(
        src_loc=src_loc,
        args=args,
        locs_mutated=results_summary.n_locs_mutated,
        locs_identified=results_summary.n_locs_identified,
        runtimes=runtimes,
    )

    trial_report = analyze_mutant_trials(results_summary.results)

    report = "\n".join([cli_report, trial_report])
    LOGGER.info("Status report: \n%s", report)

    write_report(report, args.output)
