import locale
import re
import shutil
import subprocess
import sys
from typing import Callable, Tuple


class AnalyzedObject:
    def __init__(self) -> None:
        self.defined_external_symbols = []
        self.undefined_external_symbols = []

    def contains_defined_external_symbol(self, symbol_name: str) -> bool:
        """Returns whether the given string is contained in any defined external symbol."""
        for s in self.defined_external_symbols:
            if symbol_name in s:
                return True
        return False

    def contains_undefined_external_symbol(self, symbol_name: str) -> bool:
        """Returns whether the given string is contained in any undefined external symbol."""
        for s in self.undefined_external_symbols:
            if symbol_name in s:
                return True
        return False


class ObjectAnalyzer:
    """An ObjectAnalyzer takes an object file and returns the according AnalyzedObject."""

    def analyze(self, obj_file_path: str) -> AnalyzedObject:
        """Reads the object file at the given path and returns an according AnalyzedObject. Throws if the file could not
        be read, for example, if it does not exist or has the wrong format."""
        raise NotImplementedError()


class DumpbinParser(ObjectAnalyzer):
    """Uses the Visual Studio dumpbin.exe to analyze an .obj file."""

    _SYMBOL_PATTERN = re.compile(r"^.*((UNDEF)|(SECT)).*External.*\| (.*)$")

    def __init__(self, dumpbin_caller: Callable[[str], str]) -> None:
        """Creates the DumpbinParser so that it uses the given dumpbin caller."""
        self.dumpbin_caller = dumpbin_caller

    def analyze(self, obj_file_path: str) -> AnalyzedObject:
        """Runs dumpbin and parses its output."""
        dumpbin_result = self.dumpbin_caller(obj_file_path)
        analyzed_obj = AnalyzedObject()
        for line in dumpbin_result.splitlines():
            if "warning LNK4048" in line:
                raise RuntimeError("File has invalid format.")
            match_result = DumpbinParser._SYMBOL_PATTERN.match(line)
            if match_result:
                if match_result.group(1) == "UNDEF":
                    analyzed_obj.undefined_external_symbols.append(match_result.group(4))
                else:
                    analyzed_obj.defined_external_symbols.append(match_result.group(4))
        return analyzed_obj


class DumpbinCaller:
    """A callable object that runs dumpbin.exe and returns its output."""

    def __init__(self, dumpbin_path: str) -> None:
        """Creates the DumpbinCaller so that it uses the executable at the given path."""
        self.dumpbin_path = dumpbin_path

    def __call__(self, obj_file_path: str) -> str:
        """Runs dumpbin on the given object file and returns its output."""
        return subprocess.run(
            [self.dumpbin_path, "/SYMBOLS", obj_file_path],
            stdout=subprocess.PIPE,
            encoding=locale.getdefaultlocale()[1]
        ).stdout


def create_dumpbin_analyzer(dumpbin_path: str) -> DumpbinParser:
    """Convenience function for DumpbinParser(DumpbinCaller(dumpbin_path))."""
    return DumpbinParser(DumpbinCaller(dumpbin_path))


class NmParser(ObjectAnalyzer):
    """Uses nm to analyze an .o file."""

    _SYMBOL_PATTERN = re.compile(r"^[0-9 ]* ([UT]) (.*)$")

    def __init__(self, nm_caller: Callable[[str], str]) -> None:
        """Creates the NmParser so that it uses the given nm caller."""
        self.nm_caller = nm_caller

    def analyze(self, obj_file_path: str) -> AnalyzedObject:
        """Runs nm and parses its output."""
        nm_result = self.nm_caller(obj_file_path)
        analyzed_obj = AnalyzedObject()
        for line in nm_result.splitlines():
            if line.startswith("nm:"):
                raise RuntimeError("File has invalid format.")
            match_result = NmParser._SYMBOL_PATTERN.match(line)
            if match_result:
                if match_result.group(1) == "U":
                    analyzed_obj.undefined_external_symbols.append(match_result.group(2))
                else:
                    analyzed_obj.defined_external_symbols.append(match_result.group(2))
        return analyzed_obj


def create_nm_analyzer(nm_path: str) -> NmParser:
    """Convenience function for NmParser(NmCaller(nm_path))."""
    return NmParser(NmCaller(nm_path))


class NmCaller:
    """"A callable object that runs nm and returns its output."""

    def __init__(self, nm_path: str) -> None:
        """Creates the NmCaller so that it uses the executable at the given path."""
        self.nm_path = nm_path

    def __call__(self, obj_file_path: str) -> str:
        """Runs nm on the given object file and returns its output."""
        return subprocess.run(
            [self.nm_path, "-g", obj_file_path],
            stdout=subprocess.PIPE,
            encoding=locale.getdefaultlocale()[1]
        ).stdout


def guess_win32_analyzer() -> Tuple[str, str, ObjectAnalyzer]:
    """Creates an ObjectAnalyzer for the win32 platform."""
    dumpbin_path = shutil.which("dumpbin")
    if dumpbin_path:
        return dumpbin_path, "dumpbin", create_dumpbin_analyzer(dumpbin_path)
    # TODO: Do a more elaborate search.
    raise RuntimeError("Failed to locate dumpbin executable.")


def guess_linux_analyzer() -> Tuple[str, str, ObjectAnalyzer]:
    """Creates an ObjectAnalyzer for the linux platform."""
    nm_path = shutil.which("nm")
    if nm_path:
        return nm_path, "nm", create_nm_analyzer(nm_path)
    # TODO: Do a more elaborate search.
    raise RuntimeError("Failed to locate nm executable.")


def guess_platform_specific_analyzer() -> Tuple[str, str, ObjectAnalyzer]:
    """Creates a platform specific ObjectAnalyzer. Returns a tuple (analyzer_path, analyzer_type, analyzer), where
    analyzer_path is the path to the analyzer, analyzer_type is the string with the analyzer type, and analyzer is the
    created ObjectAnalyzer. Raises a RuntimeError on failure."""
    if sys.platform == "win32":
        return guess_win32_analyzer()
    if sys.platform == "linux":
        return guess_linux_analyzer()
    raise NotImplementedError("Not implemented for the current platform.")
