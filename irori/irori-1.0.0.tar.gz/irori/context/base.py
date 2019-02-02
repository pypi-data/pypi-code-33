import enum
import platform
import os


class Os(enum.Enum):
    Linux = 'linux'
    Darwin = 'darwin'
    Windows = 'windows'
    Others = 'others'


__os = None


def _resolve_os():
    global __os
    if __os is None:
        pf = platform.system()
        pf = pf.lower()
        if 'windows' in pf:
            __os = Os.Windows
        elif 'linux' in pf:
            __os = Os.Linux
        elif 'darwin' in pf:
            __os = Os.Darwin
        else:
            __os = Os.Others
    return __os


class Context:
    @property
    def os(self):
        return _resolve_os()

    @property
    def is_posix(self):
        return os.name.lower() == 'posix'

    @property
    def is_windows(self):
        return self.os == Os.Windows

    @property
    def is_linux(self):
        return self.os == Os.Linux

    @property
    def is_darwin(self):
        return self.os == Os.Darwin
