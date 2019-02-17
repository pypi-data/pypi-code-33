import argparse
import glob
import re
import sys
from typing import Collection, Generator, Iterable, List, Optional, Pattern, Tuple

from analyze_objects.object_analyzer import create_dumpbin_analyzer, create_nm_analyzer, \
    guess_platform_specific_analyzer, ObjectAnalyzer
from analyze_objects.print_colored import init_print_colored, print_green, print_red, print_white, print_yellow


def find_symbols(
        analyzer: ObjectAnalyzer,
        def_pattern: Optional[Pattern[str]],
        undef_pattern: Optional[Pattern[str]],
        obj_paths: Collection[str]
) -> Generator[Tuple[str, Optional[List[str]], Optional[List[str]]], None, None]:
    """Uses the given analyzer to analyze all of the given object files and matches the given pattern against the symbol
    names. Yields (obj_path, def_symbols, undef_symbols), where obj_path is the path to the respective object file,
    def_symbols is the list with all defined symbols that match def_pattern (or None if def_pattern is None), and
    undef_symbols is the list with all undefined symbols that match undef_pattern (or None if undef_pattern is None)."""
    assert def_pattern is not None or undef_pattern is not None
    for obj_i, file_path in enumerate(obj_paths):
        try:
            analyzed_obj = analyzer.analyze(file_path)
        except RuntimeError:
            print_red("Failed to analyze obj file, maybe the file has an invalid format.")
            continue
        def_symbols = None
        if def_pattern:
            symbols = analyzed_obj.defined_external_symbols
            def_symbols = list(filter(def_pattern.search, symbols))
        undef_symbols = None
        if undef_pattern:
            symbols = analyzed_obj.undefined_external_symbols
            undef_symbols = list(filter(undef_pattern.search, symbols))
        yield file_path, def_symbols, undef_symbols


def create_object_analyzer(dumpbin_exe: str, nm_exe: str) -> Tuple[str, str, ObjectAnalyzer]:
    """Creates an ObjectAnalyzer for either dumpbin or nm. Tries to guess a platform specific analyzer if both
    dumpbin_exe and nm_exe are None or empty. Returns a tuple (analyzer_path, analyzer_type, analyzer)."""
    if dumpbin_exe and nm_exe:
        raise RuntimeError("Only one of dumpbin_exe and nm_exe may be non-empty.")
    if dumpbin_exe:
        return dumpbin_exe, "dumpbin", create_dumpbin_analyzer(dumpbin_exe)
    elif nm_exe:
        return nm_exe, "nm", create_nm_analyzer(nm_exe)
    else:
        try:
            return guess_platform_specific_analyzer()
        except RuntimeError as ex:
            raise RuntimeError("One of dumpbin_exe and nm_exe must be non-empty.") from ex


def find_symbols_from_cmd_line_arguments(
        dumpbin_exe: str,
        nm_exe: str,
        def_regex: str,
        undef_regex: str,
        obj_paths: Iterable[str]
) -> None:
    """Creates an ObjectAnalyzer from either dumpbin_exe or nm_exe, compiles the given regular expressions, uses glob to
    find all files that match obj_paths and finally calls find_symbols(). Prints the results."""
    # Create the correct analyzer.
    analyzer_path, analyzer_type, analyzer = create_object_analyzer(dumpbin_exe, nm_exe)

    # Check and print the arguments.
    print_green("# Setup:")
    print("Analyzer type:", analyzer_type)
    print('Analyzer executable: "{}"'.format(analyzer_path))
    if def_regex:
        print('Regular expression for defined references: "{}"'.format(def_regex))
        try:
            def_pattern = re.compile(def_regex)
        except re.error as ex:
            raise RuntimeError("Failed to compile regular expression for defined references.") from ex
    else:
        print("No regular expression for defined references given.")
        def_pattern = None
    if undef_regex:
        print('Regular expression for undefined references: "{}"'.format(undef_regex))
        try:
            undef_pattern = re.compile(undef_regex)
        except re.error as ex:
            raise RuntimeError("Failed to compile regular expression for undefined references.") from ex
    else:
        print("No regular expression for undefined references given.")
        undef_pattern = None
    if not def_pattern and not undef_pattern:
        raise RuntimeError("One of def_regex and undef_regex must be non-empty.")
    print("Object paths:", obj_paths)
    expanded_obj_paths = set()
    for obj_path in obj_paths:
        for path in glob.glob(obj_path, recursive=True):
            expanded_obj_paths.add(path)
    print("Object paths match", len(expanded_obj_paths), "files.")
    if not expanded_obj_paths:
        raise RuntimeError("The given object path does not match any file.")

    # Finally call find_symbols().
    print_green("# Analyzing object files:")
    found_symbols = find_symbols(
        analyzer,
        def_pattern,
        undef_pattern,
        expanded_obj_paths
    )
    for obj_i, (obj_path, def_symbols, undef_symbols) in enumerate(found_symbols):
        print_white('{}/{}: "{}"'.format(obj_i+1, len(expanded_obj_paths), obj_path))
        if def_symbols is not None:
            if def_symbols:
                for symbol_i, symbol in enumerate(def_symbols):
                    print_yellow("Match {}/{} (def):".format(symbol_i+1, len(def_symbols)))
                    print(symbol)
            else:
                print_white("No matches for defined references.")
        if undef_symbols is not None:
            if undef_symbols:
                for symbol_i, symbol in enumerate(undef_symbols):
                    print_yellow("Match {}/{} (undef):".format(symbol_i+1, len(undef_symbols)))
                    print(symbol)
            else:
                print_white("No matches for undefined references.")


def main(argv=None):
    """Parses the command line arguments and calls find_symbols_from_cmd_line_arguments()."""
    init_print_colored()
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument("--dumpbin_exe", type=str, help="path to the dumpbin executable")
    parser.add_argument("--nm_exe", type=str, help="path to the nm executable")
    parser.add_argument("--def_regex", type=str, help="regular expression to match defined references")
    parser.add_argument("--undef_regex", type=str, help="regular expression to match undefined references")
    parser.add_argument("obj_path", nargs="+", type=str, help="path to obj file, allows ** and * as placeholders")
    args = parser.parse_args(argv[1:])
    find_symbols_from_cmd_line_arguments(
        args.dumpbin_exe,
        args.nm_exe,
        args.def_regex,
        args.undef_regex,
        args.obj_path
    )


if __name__ == "__main__":
    sys.exit(main())
