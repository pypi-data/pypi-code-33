# coding=utf-8
"""Processing Block Controller release info."""
import logging

__subsystem__ = 'ExecutionControl'
__service_name__ = 'ProcessingBlockController'
__version_info__ = (1, 3, 1, 'a1')
__version__ = '.'.join(map(str, __version_info__[0:3]))
__pre_release__ = len(__version_info__) == 4
if len(__version_info__) == 4:
    __version__ += __version_info__[3]
__service_id__ = ':'.join(map(str, (__subsystem__,
                                    __service_name__,
                                    __version__)))
LOG = logging.getLogger('sip.ec.pbc')
