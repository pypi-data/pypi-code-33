"""Documentation for HeaderIndexer engine"""

from headerindexer.data_factory import Settings, Errors, Workings, build
from typing import List, Dict, Union


class HeaderIndexerDocs:
    """Header Indexer class.
    Call init with any optional settings, call with run(sheet_headershead_names)"""

    _settings: Settings = None
    """Dataclass for persistent settings object. Builds in init"""

    _errors: Errors = None
    """Dataclass for _error_string, _nonindexed, and _duplicates. Resets each run()"""

    _work: Workings = None
    """Dataclass for working data _sheet_headers, _head_names, _ndx_calc. Resets each run()"""

    _builder: build = build
    """init data factory object, to build above data objects"""

    def _prep_non_persistents(self, sheet_headers: List[str], head_names: Dict[str, str]) -> None:
        """Clears and sets all public dicts and lists in preparation for a fresh run"""

    def _gen_ndx_calc(self) -> None:
        """Create a dictionary using head_name keys,
        traducting head_name values into header indexes"""

    def _check_nonindexed(self) -> None:
        """Checks for any references not found, if self._settings.check_nonindexed = True"""

    def _check_duplicates(self) -> None:
        """Checks for any duplicate reference ndx, if self._settings.check_duplicates = True"""

    def _add_to_error_string(self, header: str, error_arr: Union[dict, list]) -> None:
        """Creates error string containing array causing trouble, for stderr out viewing"""

    def _raise_value_error(self) -> None:
        """Raises ValueError if allowed and needed (Nonindexed values, duplicates)"""

    def _query_fix_nonindexed(self) -> None:
        """Runs pycolims single menu for non indexed values,
        if self._settings.query_fix = True"""

    def _return_ndx_calc(self) -> Union[tuple, dict]:
        """Returns either ndx_calc or Tuple[ndx_calc, nonindexed, duplicates},
        if self._settings.return_affected = True"""

    def run(self, sheet_headers: List[str], head_names: Dict[str, str]) -> Union[tuple, dict]:
        """Run HeaderIndexer on given sheet_headers list, using head_names dict to generate a
        new nex dict containing header indexes"""
