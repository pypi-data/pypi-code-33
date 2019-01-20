import sys
import os

CORE_LINUX_OS = "linux"
CORE_MAC_OS = "darwin"

JEMU_LINUX_DIR = "jemu-linux"
JEMU_MAC_DIR = "jemu-mac"
JEMU_WINDOWS_DIR = "jemu-windows"

HERE = os.path.abspath(os.path.dirname(__file__))

JEMU_DIR = None
SSL_SO_PATH = None
if sys.platform.startswith(CORE_LINUX_OS):
    JEMU_DIR = os.path.join(HERE, 'jemu', JEMU_LINUX_DIR)
    SSL_SO_PATH = JEMU_DIR
elif sys.platform.startswith(CORE_MAC_OS):
    JEMU_DIR = os.path.join(HERE, 'jemu', JEMU_MAC_DIR)
elif os.name == 'nt':
    JEMU_DIR = os.path.join(HERE, 'jemu', JEMU_WINDOWS_DIR)


def _get_file_path(filename_without_extension):
    filename = filename_without_extension
    if os.name == 'nt':
        filename += '.exe'
    return os.path.join(JEMU_DIR, filename)


def _get_ssl_env():
    ssl_env = os.environ.copy()
    if SSL_SO_PATH:
        if "LD_LIBRARY_PATH" in ssl_env:
            ssl_env["LD_LIBRARY_PATH"] = '{}:{}'.format(ssl_env["LD_LIBRARY_PATH"], SSL_SO_PATH)
        else:
            ssl_env["LD_LIBRARY_PATH"] = SSL_SO_PATH
    return ssl_env


SSL_ENV = _get_ssl_env()
JEMU_PATH = _get_file_path('jemu')
OBJCOPY_PATH = _get_file_path('arm-none-eabi-objcopy')
OBJDUMP_PATH = _get_file_path('arm-none-eabi-objdump')
