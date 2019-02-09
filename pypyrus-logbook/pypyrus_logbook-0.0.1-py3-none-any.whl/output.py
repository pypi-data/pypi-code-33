import os

from datetime import datetime

from .formatter import Formatter

class Output():
    """
    This class represents the output including the file and the console.
    By default file output is enabled and console output is disabled.
    Parameters:
    path
        system path to the output file.
    file
        true/false for file output.
    console
        true/false for console output.
    status
        true/false for any output.
    kwargs
        collection used in file path formatter.
    """
    def __init__(
        self, log, path=None, file=True, console=False, status=True, **kwargs
    ):
        self.log = log
        app = log.app
        tmstmp = datetime.now()
        self.file = File(path, used=file, app=app, tmstmp=tmstmp, **kwargs)
        self.console = Console(used=console)
        self.status = status
        pass

    def write(self, record):
        """Direct write to the outputs."""
        if self.status is True:
            self.file.write(record)
            self.console.write(record)
        pass

    def activate(self):
        """Enable all outputs."""
        self.status = True
        pass

    def deactivate(self):
        """Disable all outputs."""
        self.status = False
        pass

class OutputRaw():
    """Base class for the outputs."""
    @property
    def used(self):
        """Status of the output."""
        return self._used

    def enable(self):
        """Enable the output."""
        self._used = True
        pass

    def disable(self):
        """Disable the output."""
        self._used = False
        pass

def _you_shall_not_pass(func):
    """
    Decorator for the methods when it is need to check the status of an output.
    """
    def wrapper(output, *args, **kwargs):
        if output.used is True:
            func(output, *args, **kwargs)
    return wrapper

class File(OutputRaw):
    """
    API to work with a file output.
    Parameters:
    path
        path to the output file. Used as a pattern for the formatter.
    used
        true/false for that output.
    kwargs
        collection used in the file path formatter.
    """
    def __init__(self, path, used=True, **kwargs):
        self._used = used
        self._set_formatter(path, **kwargs)
        self._prepare()
        pass

    @property
    def path(self):
        """Absolute path to the output file."""
        return self._path

    @property
    def IO(self):
        """IO object representing the output file interface"""
        return self._IO

    @property
    def modified(self):
        """Last time when output file was modified."""
        return self._modified

    @property
    def size(self):
        """Current output file size."""
        return self._size

    @_you_shall_not_pass
    def write(self, record):
        """
        Direct write to the output file.
        Skip if output is disabled. File stats must be refreshed.
        """
        if self._IO is None:
            self._IO = open(self._path, 'ab')
        self._IO.write(record.encode())
        self._IO.flush()
        self._modified = datetime.now()
        self._size = os.stat(self._path).st_size
        pass

    def close(self):
        """Close current file to open new."""
        self.formatter.modify(tmstmp=datetime.now())
        self._prepare()
        pass

    @_you_shall_not_pass
    def _prepare(self):
        """
        Prepare all file related attributes and objects.
        """
        self._path = os.path.abspath(self.formatter.format())
        root = os.path.dirname(self._path)
        if os.path.exists(root) is False:
            os.makedirs(root)
        self._IO = None
        self._modified = None
        self._size = None
        pass

    def _set_formatter(self, path, **kwargs):
        """Initialize the Formatter instance."""
        self.formatter = Formatter(path, **kwargs)
        pass

class Console(OutputRaw):
    """
    API to work with a console output.
    Parameters:
    used
        true/false for that output.
    """
    def __init__(self, used=True):
        self._used = used
        pass

    @_you_shall_not_pass
    def write(self, record):
        """
        Direct write to the console.
        Skip if output is disabled.
        """
        print(record, end='')
        pass
