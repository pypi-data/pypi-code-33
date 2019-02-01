from ._grrargparse_helpers import exit_handler
from ._module import APIModule
from ._grrargparser import get_instance
from . import _grrargparse_helpers as helpers

# setup tab completion and ctrl-c catcher
exit_handler()

__all__ = ['APIModule','get_instance','helpers','grr_logging']