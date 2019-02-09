import os
import sys

from datetime import datetime

from .formatter import Formatter

class Record():
    """
    This class describes the record. Record is an instance that is going
    to be logged as separated line or set of lines in the log.
    """
    def __init__(
        self, log, rectype, message, error=False,
        format=None, error_format=None, **kwargs
    ):
        self.log = log
        frame = self.__catch_frame()
        f_code = frame.f_code
        flname = f_code.co_filename
        objname = f_code.co_name

        self.tmstmp = datetime.now()
        self.isotime = self.tmstmp.isoformat(sep=' ', timespec='seconds')

        self.flname = os.path.splitext(os.path.basename(flname))[0]
        self.objname = objname if objname != '<module>' else 'main'
        self.rectype = log.RECTYPES[rectype]

        format = format or log.CONFIG['format']
        self.__rec_formatter = Formatter(format)

        self.message = message
        if error is True:
            msg_fmt = message or log.CONFIG['error_format']
        elif error is False:
            msg_fmt = message
        self.__msg_formatter = Formatter(msg_fmt, log = log, **kwargs)
        pass

    def __str__(self):
        return self.create()

    __repr__ = __str__

    def create(self):
        self.message = self.__msg_formatter.format()
        string = self.__rec_formatter.format(**self.__dict__)
        return string

    def __catch_frame(self):
        """Catch frame from file where methods of module was called."""
        frame = sys._getframe()
        module_dir = os.path.dirname(__file__)
        while True:
            if module_dir != os.path.dirname(frame.f_code.co_filename):
                return frame
            else:
                frame = frame.f_back
