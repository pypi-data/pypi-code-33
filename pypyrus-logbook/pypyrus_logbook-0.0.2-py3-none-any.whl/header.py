from .formatter import Formatter

from datetime import datetime

import platform
import socket
import pip
import sys
import os

class Header():
    """
    This class represents log header which used to record the most significant
    variables from application process. All that variables consolidated
    to internal data dictionary where key is a name of variable and its value
    is a variable meaning.
    """
    def __init__(self, log, *args, length=80, div='*', **kwargs):
        self.log = log
        self._used = False
        self.length = length
        self.div = div
        self.data = {
            'app': log.app,
            'desc': log.desc,
            'version': log.version,
            'hostname': platform.node(),
            'ip': socket.gethostbyname(socket.gethostname()),
            'user': os.getlogin(),
            'system': platform.platform(),
            'python':
                f'{platform.python_version()}-{platform.architecture()[0]}',
            'exec': sys.executable,
            'compiler': platform.python_compiler(),
            'pip': pip.__version__,
            'loctime': datetime.now().isoformat(sep=' ', timespec='seconds')
        }
        if args or kwargs:
            self.add(**kwargs)
            self.delete(*args)
        pass

    @property
    def used(self):
        """Flag to define whether header was used or not."""
        return self._used

    def create(self):
        """Main method to build formatted header in the form of string."""
        self._used = True
        ln_out, ln_in, ln_name, ln_value = self._calc_len()
        div = self.div
        data = self.data
        lines = []

        frame_fmt = '{div}{cntn:{flr}<{ln_in}}{div}\n'
        frame_formatter = Formatter(frame_fmt, div=div, ln_in=ln_in)

        top = frame_formatter.format(cntn='', flr=div)
        top += frame_formatter.format(cntn='', flr='')
        lines.append(top)

        cntn_fmt = '{name:>{ln_name}}: {value}'
        cntn_formatter = Formatter(cntn_fmt)
        for d_name, d_value in data.items():
            name = d_name.upper()
            value = d_value
            cntn = cntn_formatter.format(
                name=name, ln_name=ln_name, value=value)
            frame = frame_formatter.format(cntn=cntn, flr='')
            lines.append(frame)

        bottom = frame_formatter.format(cntn='', flr='')
        bottom += frame_formatter.format(cntn='', flr=div)
        lines.append(bottom)

        return ''.join(lines)

    def add(self, pos='start', **kwargs):
        """
        Add the variable to the data dictionary.
        Parameters:
        pos
            Describing the position of new variables in the data dictionary.
            Use "start" to insert values on top and "end" to use them on bottom.
        """
        if pos == 'start':
            self.data = {**kwargs, **self.data}
        elif pos == 'end':
            self.data = {**self.data, **kwargs}
        pass

    def delete(self, *args):
        """Delete some variables from the data dictionary to not show them."""
        for arg in args:
            del self.data[arg]
        pass

    def refresh(self):
        """Refresh dynamic values in data dictionary."""
        if hasattr(self, 'data') is True:
            if self.data.get('loctime') is not None:
                self.data['loctime'] = datetime.now().isoformat(
                    sep=' ', timespec='seconds')
        pass

    def _calc_len(self):
        """Calculate all lengths used in header formatting."""
        ln_out = self.length
        ln_in = ln_out - 2
        ln_name = max([len(key) for key in self.data.keys()]) + 3
        ln_value = ln_in - ln_name
        return (ln_out, ln_in, ln_name, ln_value)
