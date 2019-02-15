# Copyright 2018 Francesco Ceccon
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""GALINI IO logging."""
from pathlib import Path
from contextlib import contextmanager
from collections import namedtuple
import logging
import h5py
import numpy as np
from galini_io.message import (
    text_message,
    tensor_message,
    solve_start_message,
    solve_end_message,
    update_variable_message,
    add_bab_node_message,
    prune_bab_node_message,
)
from galini_io.writer import MessageWriter

CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET


LoggingContext = namedtuple('LoggingContext', ['solver', 'run_id'])


class RootLogger(object):
    """RootLogger class for rich log messages.

    If `directory` is `None`, then rich logging will be disabled.
    This object keeps referenecs to the Python logger and output
    files, but does not provide any method to write to them.
    Instantiate a child logger for each solver/run instead.

    Parameters
    ----------
    config : dict-like
        logging configuration
    """
    def __init__(self, config):
        self.config = config
        self.has_rich_logging = False
        self.apply_config(config)

    def apply_config(self, config):
        """Apply config to logger."""
        if config is None:
            config = {}

        level_name = config.get('level', 'INFO')
        self.level = logging.getLevelName(level_name)

        # delegate some logs to python logging module
        self._pylogger = logging.Logger(__name__)
        self._pylogger.setLevel(self.level)
        if config.get('stdout', False):
            stream_handler = logging.StreamHandler()
            self._pylogger.addHandler(stream_handler)

        if config.get('file') is not None:
            file_handler = logging.FileHandler(config['file'])
            self._pylogger.addHandler(file_handler)

        self._setup_message_log(config)

    def children_directory(self, ctx):
        children_directory = '{}_{}'.format(ctx.solver, ctx.run_id)
        return self.directory / children_directory

    def file_path(self, filename):
        """Full path for filename inside logger output dir.

        Parameters
        ----------
        filename : string
            file name

        Returns
        -------
        path or None
            Returns None if rich logging is disabled
        """
        if not self.has_rich_logging:
            return None
        path = self.directory / filename
        return str(path)

    @contextmanager
    def child_logger(self, solver, run_id):
        child_ctx = LoggingContext(solver, run_id)
        logger = Logger(ctx=child_ctx, root=self)
        yield logger

    def _setup_message_log(self, config):
        directory = config.get('directory', None)
        if not directory:
            self.has_rich_logging = False
            return
        self.has_rich_logging = True
        self.directory = Path(directory)
        if not self.directory.exists():
            self.directory.mkdir(exist_ok=True)
        self.messages_file = open(self.directory / 'messages.bin', 'wb')
        self.writer = MessageWriter(self.messages_file)
        self.data_filename = 'data.hdf5'
        self.data_file = h5py.File(str(self.directory / self.data_filename), 'w')

    def _log_message(self, message):
        if not self.has_rich_logging:
            return
        self.writer.write(message)

    def _log(self, ctx, lvl, msg, *args, **kwargs):
        if lvl < self.level:
            return
        fmt_msg = msg.format(*args, **kwargs)
        # scrip newline because it's added by pylogger
        if fmt_msg[-1] == '\n':
            pylog_fmt_msg = fmt_msg[:-1]
        else:
            pylog_fmt_msg = fmt_msg
        self._pylogger.log(
            lvl,
            '[{}][{}] {}'.format(ctx.solver, ctx.run_id, pylog_fmt_msg),
        )

        message = text_message(ctx.solver, ctx.run_id, fmt_msg, level=lvl)
        self._log_message(message)

    def _tensor(self, ctx, group, dataset, data):
        if not self.has_rich_logging:
            return
        group = '{}/{}/{}'.format(ctx.solver, ctx.run_id, group)
        if group is None:
            h5_group = self.data_file
        else:
            if group not in self.data_file:
                self.data_file.create_group(group)
            h5_group = self.data_file[group]
        if dataset not in h5_group:
            data = np.array(data, dtype=np.float)
            h5_group.create_dataset(dataset, data=data)
            message = tensor_message(
                ctx.solver,
                ctx.run_id,
                filename=self.data_filename,
                group=group,
                dataset=dataset,
                sizes=np.shape(data),
            )
            self._log_message(message)

    def __del__(self):
        if self.has_rich_logging:
            try:
                self.messages_file.close()
                self.data_file.close()
            except:
                pass


class Logger(object):
    def __init__(self, ctx, root):
        self.ctx = ctx
        self._root = root

    @staticmethod
    def from_kwargs(kwargs):
        logger = kwargs.pop('logger', None)
        if logger:
            return logger
        return NullLogger()

    @contextmanager
    def child_logger(self, solver, run_id):
        child_ctx = LoggingContext(solver, run_id)
        logger = Logger(ctx=child_ctx, root=self._root)
        yield logger

    def log_message(self, message):
        """Log message to disk."""
        self._root._log_message(message)

    def debug(self, msg, *args, **kwargs):
        """Log msg with DEBUG level."""
        return self.log(DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Log msg with INFO level."""
        return self.log(INFO, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Log msg with WARNING level."""
        return self.log(WARNING, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Log msg with ERROR level."""
        return self.log(ERROR, msg, *args, **kwargs)

    def log(self, lvl, msg, *args, **kwargs):
        """Log msg with lvl level and unique run id.

        Arguments
        ---------
        lvl: int
            logging level
        msg: str
            format string
        args: Any
            arguments passed to msg.format
        kwargs: Any
            keyword arguments passed to msg.format
        """
        self._root._log(self.ctx, lvl, msg, *args, **kwargs)

    def log_solve_start(self):
        self.log_message(solve_start_message(
            solver=self.ctx.solver,
            run_id=self.ctx.run_id,
        ))

    def log_solve_end(self):
        self.log_message(solve_end_message(
            solver=self.ctx.solver,
            run_id=self.ctx.run_id,
        ))

    def log_add_bab_node(self, coordinate, lower_bound, upper_bound, branching_variables=None):
        self.log_message(add_bab_node_message(
            solver=self.ctx.solver,
            run_id=self.ctx.run_id,
            coordinate=coordinate,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            branching_variables=branching_variables,
        ))

    def log_prune_bab_node(self, coordinate):
        self.log_message(prune_bab_node_message(
            solver=self.ctx.solver,
            run_id=self.ctx.run_id,
            coordinate=coordinate,
        ))

    def update_variable(self, name, iteration, value):
        self.log_message(update_variable_message(
            solver=self.ctx.solver,
            run_id=self.ctx.run_id,
            name=name,
            iteration=iteration,
            value=value,
        ))

    def tensor(self, group, dataset, data):
        """Log tensor data to data file, if configured.

        Arguments
        ---------
        group : string
            dataset group
        dataset : string
            dataset name
        data : array-like
            the data to log
        """
        return self._root._tensor(self.ctx, group, dataset, data)


class NullLogger(Logger):
    """A logger that does not log anything."""
    def __init__(self):
        self.has_rich_logging = False

    def log_message(self, message):
        pass

    def tensor(self, group, dataset, data):
        pass

    def log(self, lvl, msg, *args, **kwargs):
        pass

    def log_solve_start(self):
        pass

    def log_solve_end(self):
        pass

    def log_add_bab_node(self, coordinate, lower_bound, upper_bound, branching_variables):
        pass

    def log_prune_bab_node(self, coordinate):
        pass

    def update_variable(self, name, iteration, value):
        pass

    @contextmanager
    def child_logger(self, solver, run_id):
        yield NullLogger()
