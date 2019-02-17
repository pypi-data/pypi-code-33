"""Documentation for data factory classes"""

from typing import List as _List, Dict as _Dict


class ErrorsDocs:
    """Base object for error string and dicts. Build and set with Factory
    Included reset function"""

    stderr: str = '\n'
    """Error string, to be stderr (dependant on self._settings.raise_error)"""

    nonindexed: _List[str] = []
    """Dict of reference headers that were not found in self.sheet_headers"""

    duplicates: _Dict[str, int] = []
    """Dict of reference headers that were found more than once"""

    def reset(self):
        """Resets all Error holders to default"""


class ErrorsFactoryDocs:
    """Factory to generate an Errors object for HeaderIndexer"""

    @staticmethod
    def _return_errors_obj():
        """Return new Errors object"""

    def new_errors_obj(self):
        """Call to build, init, and return a new errors object"""


# ---------------------------------------------------


class SettingsDocs:
    """Base object for HeaderIndexer boolean flags. Build and set with Factory"""

    raise_error = False
    """Raise ValueError If any non_indexed or duplicate headers are found. If true, no query to fix 
    and nothing will return"""

    return_affected = False
    """Returns Tuple[dict] (ndx_calc, non_indexed, duplicates)"""

    check_nonindexed = True
    """Gathers non_indexed headers into Dict[str, int]"""

    check_duplicates = False
    """Gathers duplicate headers into Dict[str, int]"""

    prompt_fix = True
    """Call single stage menu to fix non indexed headers by Id-ing proper headers
    Note, at this time it does not check for duplicate headers"""

    def reset(self,
              raise_error=False,
              return_affected=False,
              check_nonindexed=True,
              check_duplicates=False,
              prompt_fix=True):
        """Resets headerIndexer settings"""


class SettingsFactoryDocs:
    """Factory to generate a settings object for HeaderIndexer"""

    @staticmethod
    def _return_settings_obj(raise_error,
                             return_affected,
                             check_nonindexed,
                             check_duplicates,
                             prompt_fix):
        """Return new settings object"""

    def new_settings_obj(self,
                         raise_error=False,
                         return_affected=False,
                         check_nonindexed=True,
                         check_duplicates=False,
                         prompt_fix=True):
        """Call to build, init, and return a new errors object"""


# ---------------------------------------------------


class WorkingsDocs:
    """Base object for working list and dicts. Build and set with Factory"""

    sheet_headers_indexes: _Dict[str, int] = {}
    """Dict of all sheet_headers and their enumerated indexes"""

    head_names: _Dict[str, str] = {}
    """Reference dictionary, to covert to ndx_calc"""

    ndx_calc: _Dict[str, int] = {}
    """Dictionary to return; converted from self.head_names with values traducted to indexes"""

    def reset(self, sheet_headers: _List[str], head_names: _Dict[str, str]):
        """Resets all attributes. Requires sheet_headers and head_names"""


class WorkingsFactoryDocs:
    """Factory to generate a Workings object for HeaderIndexer"""

    @staticmethod
    def _return_workings_obj():
        """Return new Workings object"""

    # def new_workings_obj(self, sheet_headers: _List[str], head_names: _Dict[str, str]):
    def new_workings_obj(self):
        """Call to build, init, and return a new errors object"""
