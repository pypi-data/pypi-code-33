import sys
import six
import os

from rook.logger import logger

if sys.platform in ('darwin', 'linux2', 'linux'):

    hook_installed = False
    original_os_fork = None

    import native_extensions

    def os_fork_hook():
        try:
            six.print_("[Rookout] Rookout does not support running in forking processes. Shutting down.")

            from .singleton import singleton_obj
            singleton_obj.stop()

            native_extensions.python_fork_handler_called = 1

        except:
            pass

        return original_os_fork()

    def install_fork_handler():
        global hook_installed
        if hook_installed:
            return
        hook_installed = True

        native_extensions.RegisterPreforkCallback()

        logger.debug("Installing os.fork handler")
        global original_os_fork
        original_os_fork = os.fork
        os.fork = os_fork_hook

else:
    def install_fork_handler():
        pass
