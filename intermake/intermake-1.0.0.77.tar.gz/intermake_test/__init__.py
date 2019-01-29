"""
Intermake test suite and commands.

Loading this package adds the test commands to the base intermake application.

The __main__ function of this package defers to Intermake, showing the
Intermake base application with the test commands pre-loaded.

There are no public exports.

To run the full Intermake test suite launch::

    python -m intermake_test run_tests
"""

from . import commands as _
