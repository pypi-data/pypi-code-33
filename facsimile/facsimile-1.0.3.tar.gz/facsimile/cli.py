
import os
import sys
from optparse import OptionParser, OptionGroup

options = {
    'devel': {
        'action': 'store_true',
    }
}

default_top_dir = os.path.join(os.getcwd(), '.facsimile')

def option_parser(derived, usage=None):
    if not usage:
        usage = "usage: %prog [options] <release environment> [<version>]"

    parser = OptionParser(usage=usage)
    parser.add_option("--devel", action="store_true", dest="devel",
                      help="build against development, force skip deploy")
    parser.add_option("--chatty", action="store_true", dest="chatty",
                      help="announce via al, even when not a production push")
    parser.add_option("-C", "--clean", action="store_true",
                      dest="clean", help="clean all temporary files")
    parser.add_option("-d", "--debug", action="store_true",
                      dest="debug", help="display debug information")
    parser.add_option(
        "-n", "--dry-run", action="store_true", dest="dry_run", help="just print commands")
    parser.add_option(
        "--skip-env-check", action="store_true", help="Skip environment check")

#        targets = derived.get_defined_targets(derived)
# TODO fix on dat preload before opt
    targets = []
    parser.add_option("--target-only", dest="target_only",
                      help="Deploy to target group: %s" % (', '.join(targets)))
    parser.add_option("--top-dir", dest="top_dir", metavar='DIR', default=default_top_dir,
                      help="use this for top directory to generate files and save state (default %s)" % default_top_dir)

    group = OptionGroup(parser, "Data options")
    group.add_option(
        "--write-codec", help="use this for writing data (default is definition codec)", metavar="CODEC")
    group.add_option(
        "--force-codec", help="force codec for reading and writing (will not load any data not using this type) NOT IMPL", metavar="CODEC")
    parser.add_option_group(group)

    group = OptionGroup(parser, "Directory overrides")
    group.add_option(
        "--src-dir", dest="src_dir", help="use for src_dir (implies devel)", metavar="DIR")
    parser.add_option_group(group)

    group = OptionGroup(parser, "Informational options", "display only, no execution")
    group.add_option("--list-codecs", action="store_true",
                      dest="just_list_codecs", help="just list codecs")
    group.add_option("--list-nodes", action="store_true",
                      dest="just_list_nodes", help="just list nodes")
    group.add_option("--summary", action="store_true",
                      dest="just_summary", help="show summary and paths")
    parser.add_option_group(group)

    stages = getattr(derived, 'stages', [])
    if stages:
        group = OptionGroup(parser, "Stage options",
                            "Stages: " + " ".join(stages))
        group.add_option(
            "--start", dest="start", help="start at this stage", metavar="STAGE")
        group.add_option(
            "--end", dest="end", help="end at this stage", metavar="STAGE")
        group.add_option(
            "--only", dest="only", help="only process this stage", metavar="STAGE")
        parser.add_option_group(group)

    group = OptionGroup(parser, "Build options")
    group.add_option(
        "--bits", dest="bits", help="how many bits to target: 32 or 64", metavar="BITS")
    group.add_option(
        "--compiler", dest="compiler", help="use this compiler", metavar="CC")
    group.add_option("--debuginfo", action="store_true",
                     dest="debuginfo", help="include debug info")
    group.add_option("--build-docs", action="store_true",
                     dest="build_docs", help="include build of documentation (linux only)")
    group.add_option("--static", action="store_true", dest="static",
                     help="do a static runtime build (windows only)")
    group.add_option("-j", dest="j", default=12,
                     help="Concurrency for make. Not used by everything. Defaults to 12.")
    group.add_option("--release", action="store_true", dest="release",
                     help="do a release runtime build")
    group.add_option(
        "--test-config", dest="test_config", help="test config file", metavar="FILE")
    group.add_option(
        "--skip-unit", action="store_true", dest="skip_unit", help="skip unit tests")
    group.add_option(
        "--skip-libcheck",
        action="store_true",
        default=False,
        dest="skip_libcheck",
        help="Force deploy to skip the libcheck stage. Libcheck is not enabled on all stages. Not advised for production pushes.")
    group.add_option("--ccache", action="store_true", dest="use_ccache",
                     default=False, help="Use ccache. Not obeyed by all builds.")
    parser.add_option_group(group)

    if hasattr(derived, 'additional_options'):
        group = OptionGroup(parser, "Additional Options")
        derived.additional_options(group)
        parser.add_option_group(group)

    return parser

def pop_first_arg(argv):
    """
    find first positional arg (does not start with -), take it out of array and return it separately
    returns (arg, array)
    """
    for arg in argv:
        if not arg.startswith('-'):
            argv.remove(arg)
            return (arg, argv)

    return (None, argv)

def check_options(options, parser):
    """
    check options requirements, print and return exit value
    """
    if not options.get('release_environment', None):
        print "release environment is required"
        parser.print_help()
        return os.EX_USAGE

    return 0

def check_info(options, inst):
    info = False
    if options.get('just_list_codecs', False):
        inst.print_list_nodes()
        info = True
    if options.get('just_list_nodes', False):
        inst.print_list_nodes()
        info = True
    if options.get('just_summary', False):
        inst.print_summary()
        info = True

    return info

def parse_options(cls, argv=sys.argv[1:], usage=None):
    try:
        parser = option_parser(cls, usage)
        # default value for return from catch
        options = {}
        (options, args) = parser.parse_args(argv)

        try:
            options.release_environment = args[0]
            options.version = args[1]

        except IndexError:
            pass

        options = vars(options)
        return (check_options(options, parser), options)

    except SystemExit as e:
        return (e.code, options)

def instantiate(cls, options):
    return cls(**options)

def main(cls, argv=sys.argv[1:], run=True):
    (status, options) = parse_options(cls, argv)
    if status:
        return status

    inst = instantiate(cls, options)

    info = check_info(options, inst)

    if run and not info:
        inst.run()
    return 0

