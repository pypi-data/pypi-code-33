# (C) Datadog, Inc. 2018
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

import json
from contextlib import closing
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from pylint.lint import PyLinter, fix_import_path
from pylint.reporters.json import JSONReporter


def validate_py3(path_to_module):
    """
    Run pylint python3 validation on the python module/package provided
    """
    with closing(StringIO()) as out:
        linter = PyLinter(reporter=JSONReporter(output=out))
        linter.load_default_plugins()
        linter.python3_porting_mode()
        # Disable `no-absolute-import`, which checks for a behaviour that's already part of python 2.7
        # cf https://www.python.org/dev/peps/pep-0328/
        linter.disable("no-absolute-import")
        with fix_import_path([path_to_module]):
            linter.check(path_to_module)
            linter.generate_reports()
        raw_results = json.loads(out.getvalue() or "{}")

    results = []
    for problem in raw_results:
        # An issue found by pylint is a dict like
        # {
        #     "message": "Calling a dict.iter*() method",
        #     "obj": "OpenFilesCheck.check",
        #     "column": 27,
        #     "path": "/path/to/file.py",
        #     "line": 235,
        #     "message-id": "W1620",
        #     "type": "warning",
        #     "symbol": "dict-iter-method",co
        #     "module": "file"
        # }
        results.append(
            {
                "message": "Line {}, column {}: {}".format(problem["line"], problem["column"], problem["message"]),
                "path": problem["path"],
            }
        )

    return results
