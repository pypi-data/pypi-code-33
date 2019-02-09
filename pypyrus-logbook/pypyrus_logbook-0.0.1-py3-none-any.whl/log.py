import os
import sys
import time
import platform
import traceback

from datetime import datetime

from .email import Email
from .header import Header
from .output import Output
from .record import Record
from .sysinfo import Sysinfo
from .formatter import Formatter
from .errors import StatusException


class Log():
    """Main API for using and managing the logs."""
    def __init__(
        self, app, desc=None, version=None,
        status=True, file=True, console=False, control=True,
        folder=None, filename=None, extension=None,
        format=None, length=80, div='*', error_format=None,
        err_formatting=True, alarming=True, limit_by_size=True,
        max_size=1024*1024*10, limit_by_day=True, email=False, ip=None,
        port=None, user=None, password=None, tls=True, recipients=None
    ):
        # Attributes describing the application.
        self.__app = app
        self.__desc = desc
        self.__version = version

        # Some log important attributes
        self.__control = control
        self.__open_time = datetime.now()

        # Global log config.
        self.CONFIG = {}

        # Default messages.
        self.MESSAGES = {
            'ok': 'OK',
            'success': 'SUCCESS',
            'fail': 'FAIL',
            'sos': 'SOS! ERROR CAUSED AN EXIT FROM THE PROGRAM.'
        }

        self.RECTYPES = {
            'none': 'NONE',
            'info': 'INFO',
            'debug': 'DEBUG',
            'warning': 'WARNING',
            'error': 'ERROR',
            'critical': 'CRITICAL'
        }

        folder = folder or 'logs'
        filename = filename or '{app}_{tmstmp:%Y%m%d%H%M%S}'
        extension = extension or 'log'
        format = format or '{isotime}\t{rectype}\t{message}\n'
        error_format = error_format or '{err_name} - {err_value} - {err_file} - {err_line} - {err_obj}'

        # Complete the initial configuration.
        self.configure(
            file=file, console=console, status=status,
            folder=folder, filename=filename, extension=extension,
            format=format, length=length, div=div, error_format=error_format,
            err_formatting=err_formatting, alarming=alarming,
            limit_by_size=limit_by_size, max_size=max_size,
            limit_by_day=limit_by_day, email=email, ip=ip, port=port,
            user=user, password=password, tls=tls, recipients=recipients,
            emergency=2)
        pass

    # Getters for private variables.
    @property
    def app(self):
        return self.__app

    @property
    def desc(self):
        return self.__desc

    @property
    def version(self):
        return self.__version

    @property
    def control(self):
        return self.__control

    @property
    def open_time(self):
        return self.__open_time

    @property
    def status(self):
        return self.__status

    def configure(
        self, file=None, console=None, status=None,
        folder=None, filename=None, extension=None,
        format=None, error_format=None, err_formatting=None, alarming=None,
        length=None, div=None, limit_by_size=None, max_size=None,
        limit_by_day=None, email=None, ip=None, port=None, user=None,
        password=None, tls=None, recipients=None, emergency=None
    ):
        """
        Main method to configure the log.
        Entered parameters are recognizing automatically.
        Some of the parameters are not allowed to modify due to intersection
        with important log variables. They will be skipped if detected.
        After recognized parameters has been updated only new remain.
        All new will be stored to forms.
        When all parameters are in place necessary updates will run.
        """
        # Local links to configuration.
        config = self.CONFIG
        messages = self.MESSAGES

        # Configure the output.
        if file is not None:
            config['file'] = file
        if console is not None:
            config['console'] = console
        if status is not None:
            config['status'] = status
        if folder is not None:
            config['folder'] = folder
        if filename is not None:
            config['filename'] = filename
        if extension is not None:
            config['extension'] = extension

        # Case for first instance initialization.
        if hasattr(self, 'output') is False:
            path = f'{folder}/{filename}.{extension}'
            self.output = Output(
                self, path=path, file=file, console=console, status=status)
        else:
            if status is not None:
                if status is True:
                    self.output.activate()
                elif status is False:
                    self.output.deactivate()
            if file is not None:
                if file is True:
                    self.output.file.enable()
                elif file is False:
                    self.output.file.disable()
            if console is not None:
                if console is True:
                    self.output.console.enable()
                elif console is False:
                    self.output.console.disable()
            if folder or filename or extension is not None:
                n_folder = folder or config['folder']
                n_filename = filename or config['filename']
                n_extension = extension or config['extension']
                path = f'{n_folder}/{n_filename}.{n_extension}'
                self.output.file.formatter.modify(pattern=path)
                self.restart()

        # Case for first instance initialization.
        if hasattr(self, 'email') is False:
            self.email = Email(
                self, address=email, ip=ip, port=port, user=user,
                password=password, tls=tls, recipients=recipients)

        if hasattr(self, 'sysinfo') is False:
            self.sysinfo = Sysinfo(self)

        if hasattr(self, 'header') is False:
            self.header = Header(self)

        if format is not None:
            config['format'] = format
        if error_format is not None:
            config['error_format'] = error_format
        if length is not None:
            config['length'] = length
            self.header.length = length
        if div is not None:
            config['div'] = div
            self.header.div = div
        if err_formatting is not None:
            config['err_formatting'] = err_formatting
        if alarming is not None:
            config['alarming'] = alarming
        if limit_by_size is not None:
            config['limit_by_size'] = limit_by_size
        if max_size is not None:
            config['max_size'] = max_size
        if limit_by_day is not None:
            config['limit_by_day'] = limit_by_day
        if emergency is not None:
            config['emergency'] = emergency

        pass

    def write(self, string):
        """Direct write to the output."""
        self.check()
        self.output.write(string)
        pass

    def record(self, rectype, message, error=False, **kwargs):
        """
        Basic method and an interface for recording.
        By default it writes the records with the type NONE.
        That can be changed but depends on available record types.
        Local forms can be passed through the kwargs.
        They will have higher priority than forms from global config.
        """
        record = Record(self, rectype, message, error=error, **kwargs)
        string = record.create()
        self.write(string)
        pass

    def info(self, message, **kwargs):
        """Record an info message."""
        rectype = 'info'
        self.record(rectype, message, **kwargs)
        pass

    def debug(self, message, **kwargs):
        """Record a message containing debug information."""
        rectype = 'debug'
        self.record(rectype, message, **kwargs)
        pass

    def error(
        self, message=None, rectype='error', level=1,
        formatting=None, alarming=None, sos=None, **kwargs
    ):
        """
        Record an error message.
        If the exception was found then transform it to the forms.
        Send alarm notification if email is configurated.
        Abort the application in case of high level error.
        """
        config = self.CONFIG
        messages = self.MESSAGES
        if formatting is None:
            formatting = config['err_formatting']
        if alarming is None:
            alarming = config['alarming']

        # Parse the error.
        err_type, err_value, err_tb = sys.exc_info()
        if err_type is not None:
            if formatting is True:
                err_name = err_type.__name__
                err_value = err_value

                for tb in traceback.walk_tb(err_tb):
                    f_code = tb[0].f_code

                    err_file = os.path.abspath(f_code.co_filename)
                    err_line = tb[1]
                    err_obj = f_code.co_name

                    self.record(
                        rectype, message, error=True,
                        err_name=err_name, err_value=err_value,
                        err_file=err_file, err_line=err_line,
                        err_obj=err_obj, **kwargs)
            elif formatting is False:
                exception = traceback.format_exception(
                    err_type, err_value, err_tb)
                message = '\n'
                message += ''.join(exception)
                self.record(rectype, message, **kwargs)
        else:
            message = message or ''
            self.record(rectype, message, **kwargs)

        # Inform about the error.
        if alarming is True:
            if self.email.used is True:
                self.email.alarm()

        # Break execution in case of critical error if permitted.
        if self.__control is True:
            if level >= config['emergency']:
                sos = sos or messages['sos']
                self.record(rectype, sos, **kwargs)
                sys.exit()
        pass

    def warning(self, message=None, **kwargs):
        """Shortcut for warning (level = 0)."""
        self.error(message, rectype='warning', level=0, **kwargs)
        pass

    def critical(self, message=None, **kwargs):
        """Shortcut for critical error (level = 2)."""
        self.error(message, rectype='critical', level=2, **kwargs)
        pass

    def head(self):
        """Generate header and record it to the output."""
        string = self.header.create()
        self.write(string)
        pass

    def subhead(self, string):
        """
        Generate subhead as upper-case text between two border lines and
        record it to the output.
        """
        string = f'\t{string}\n'.upper()
        self.bound()
        self.write(string)
        self.bound()
        pass

    def bound(self, div=None, length=None):
        """
        Draw horizontal border.
        Useful when need to separate different log blocks.
        """
        length = self.CONFIG['length']
        div = self.CONFIG['div']
        border = div * length
        border += '\n'
        self.write(border)
        pass

    def blank(self, number=1):
        """Write blank lines."""
        string = '\n'*number
        self.write(string)

    def ok(self, **kwargs):
        """Record an ok message."""
        rectype = 'info'
        message = self.MESSAGES['ok']
        self.record(rectype, message, **kwargs)
        pass

    def success(self, **kwargs):
        """Record a success message."""
        rectype = 'info'
        message = self.MESSAGES['success']
        self.record(rectype, message, **kwargs)
        pass

    def fail(self, **kwargs):
        """Record a fail message."""
        rectype = 'info'
        message = self.MESSAGES['fail']
        self.record(rectype, message, **kwargs)
        pass

    def restart(self):
        """Open new output file to continue the logging."""
        self.__open_time = datetime.now()
        if self.output.file.used is True:
            self.output.file.close()
        if self.header.used is True:
            self.header.refresh()
            self.head()
        pass

    def check(self):
        """
        Check the output file statistics to catch when current file must be
        closed and new one must be opened.
        """
        config = self.CONFIG
        if self.output.file.used is True:
            if config['limit_by_size'] is True:
                if self.output.file.size is not None:
                    if self.output.file.size > config['max_size']:
                        self.restart()
                        return
            if config['limit_by_day'] is True:
                if self.output.file.modified is not None:
                    if self.output.file.modified.day != datetime.now().day:
                        self.restart()
                        return
