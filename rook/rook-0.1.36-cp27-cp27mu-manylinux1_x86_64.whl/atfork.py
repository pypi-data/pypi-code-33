import sys
import os
import logging

if sys.platform in ('darwin', 'linux2', 'linux'):
    hook_installed = False
    original_os_fork = os.fork

    import native_extensions
    native_extensions.python_fork_handler_called = 1

    def os_fork_hook():
        try:
            from .singleton import singleton_obj
            singleton_obj._agent_com.stop(final=False)

        except:
            pass

        # Set "called" flag, to be checked in the
        # pthread_atfork, and reset after
        native_extensions.python_fork_handler_called = 1
        pid = original_os_fork()
        native_extensions.python_fork_handler_called = 0

        try:
            from .singleton import singleton_obj

            if pid == 0:
                # child

                # remove all log handlers since they lock
                for handler in logging.getLogger("rook").handlers:
                    logging.getLogger("rook").removeHandler(handler)

                # don't leave child with patches
                singleton_obj._agent_com._aug_manager._trigger_services.clear_augs()

                # restore original fork
                os.fork = original_os_fork
            else:
                # parent
                singleton_obj._agent_com.connect_to_agent()
        except:
            pass

        return pid

    def install_fork_handler():
        global hook_installed, original_os_fork

        if hook_installed:
            return

        hook_installed = True

        native_extensions.RegisterPreforkCallback()

        os.fork = os_fork_hook

else:
    def install_fork_handler():
        pass
