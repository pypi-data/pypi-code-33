"""
Intermake debugging commands.

If this modules is loaded then the debug commands become available in all intermake `Application`s.
"""

from .commands import debug_eval, debug_coercers, debug_css, debug_echo, debug_echo_numeric, debug_error, debug_modules, debug_set, debug_which
