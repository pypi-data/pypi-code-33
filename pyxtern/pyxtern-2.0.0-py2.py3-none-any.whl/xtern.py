"""
:mod:`pyxtern.xtern` provides different ways to run an external command
synchronously. They all rely on the :func:`run` function so it is worth
giving a look at its documentation.

"""

import functools as ft
import logging as lg
import os.path as op
import subprocess as sp
import sys
import threading as th

from pyxtern.utils import temporary_directory, _log_to_streams, _check_cmd

logs = lg.getLogger(__name__)


class Cmd(list):
    """
    Create a list formatted external command.

    Create a list formatted external command based on argument templates and
    allow provides an easy way to run it either synchronously or
    asynchronously.

    **Usages:**
        >>> c = Cmd()
        >>> c.add_arg(...)
        >>> c.run()

    """

    def __init__(self, cmd=None):
        """
        **Args:**
            cmd (:obj:`str`): The basic external command.

        """
        super().__init__()
        self.append(cmd)

    def append(self, object):
        """
        Append an object to the command list.

        **Args:**
            object (:obj:`object`): The object to append to the list.

        """
        super().append(object)
        return self

    def extend(self, iterable):
        """
        Extend the command list.

        **Args:**
            iterable (:obj:`iterable`): The :obj:`iterable` to append to the
                list.

        """
        super().extend(iterable)
        return self

    def add_arg(
            self,
            kwargs=None,
            val=None,
            arg=None,
            alias=None,
            prefix="",
            suffix=None,
            flag=False,
            default=None):
        """
        Add a formatted argument to the command list.

        **Args:**
            kwargs (:obj:`dict`): The dictionary from which the argument value
                should be extracted.

            val (:obj:`object` | :obj:`list`): The value(s) of the argument.

            arg (:obj:`str`): The argument as it should appear in the command.

            alias (:obj:`str`): The name of the argument inside of kwargs
                dictionary.

            prefix (:obj:`str`): The prefix to put before the argument in the
                command line.

            suffix (:obj:`str`): The suffix to put between the argument and its
                value in the command line.

            flag (:obj:`bool`): If set to :obj:`True`, the argument is a flag.
                If set to :obj:`False`, the argument is added with its value.

            default (:obj:`object`): The default value of the argument if not
                found inside of the kwargs dictionary.

        **Note:**
            If val is set, kwargs won't be used.

        **Usages:**
            >>> c = Cmd().add_arg()
            >>> c.add_arg()
        """
        param = "{}{}".format(prefix, arg)
        if kwargs or val:
            # Get value
            if kwargs and not val:
                if alias:
                    val = kwargs.pop(alias, default)
                else:
                    val = kwargs.pop(arg, default)
            if flag:
                # Create arg string
                if val:
                    self.append(param)
            else:
                # Format value
                if val:
                    if isinstance(val, list):
                        val = " ".join(list(map(str, val)))
                    else:
                        val = str(val)
                    # Create arg string
                    if suffix:
                        param = "{}{}{}".format(param, suffix, val)
                        self.append(param)
                    else:
                        self.extend([param, val])
        return self

    def add_args(
            self,
            kwargs=None,
            args=None,
            prefix="",
            suffix=None,
            flag=False,
            default=None):
        """
        Add several formatted arguments to the command list.

        **Args:**
            args (:obj:`list` | :obj:`dict`): If args is a :obj:`list`, it
                should contain the arguments as they should be added to the
                command line. If args is a :obj:`dict`, the key of each arg
                should be the key inside of kwargs and the value should be the
                arguments as they should be added to the command line.

        **See also:**
            :func:`add_arg`
                Refer to the :func:`add_arg` method for more information on
                the other parameters.

        **Usages:**
            >>> c = Cmd().add_args()
            >>> c.add_args()
        """
        if kwargs:
            if isinstance(args, list):
                for arg in args:
                    self.add_arg(
                        kwargs=kwargs,
                        arg=arg,
                        prefix=prefix,
                        suffix=suffix,
                        flag=flag,
                        default=default
                    )
            elif isinstance(args, dict):
                for alias, arg in args.items():
                    self.add_arg(
                        kwargs=kwargs,
                        arg=arg,
                        alias=alias,
                        prefix=prefix,
                        suffix=suffix,
                        flag=flag,
                        default=default
                    )
        return self

    def run(self, **kwargs):
        """
        Run the external command.

        **See also:**
            :func:`run <xtern.run>`
                The :func:`run <xtern.run>` function is called so refer to its
                documentation for more information.

        **Usages:**
            >>> c = Cmd().run()
            >>> c.run()

        **Example:**
            >>> c = Cmd("find").append("./pyxtern")
            >>> c.add_arg(arg="name", prefix="-", val="*.py")
            >>> c.run(tee=True)
            ./pyxtern/xtern.py
            ./pyxtern/__init__.py
            ./pyxtern/utils.py

        """
        return run(self, **kwargs)


def run_sync(cmd, **kwargs):
    """
    Run an external command synchronously.

    Run an external command synchronously and return its exit code, standard
    output and standard error.

    **Args:**
        cmd (:obj:`list`): The list formatted command to run.

        tee (:obj:`bool`): If set to :obj:`True`, redirect standard output and
            standard error streams from external function to current standard
            output and standard error streams.

        log (:obj:`tuple`): Streams where external function standard output and
            standard error should be redirected to. Can be either
            ``(out, err)`` or ``([outs], [errs])``.

        timeout(:obj:`float`): The maximum amount of time the process has to
            finish (in seconds). If the timeout is reached, the process is
            killed and a :obj:`TimeoutError <subprocess.TimeoutError>` is
            raised.

        \**kwargs: Arguments that should be given to the
            :func:`temporary_directory() <utils.temporary_directory>` function.

    **Returns:**
        :obj:`int`: The exit code of the external function.

        :obj:`str`: The standard output of the external function.

        :obj:`str`: The standard error of the external function.

    **Raises:**
        :obj:`FileNotFoundError`
            Occurs when trying to access a non-existent file or directory.

        :obj:`TimeoutExpired <subprocess.TimeoutExpired>`
            Occurs when the process reaches the timeout limit.

        :obj:`CalledProcessError <subprocess.CalledProcessError>`
            Occurs when the external command line returns non-zero exit code.

    **See also:**
        :class:`Popen <subprocess.Popen>`
            For more information on possible raised exceptions, refer to
            :class:`Popen <subprocess.Popen>` class.

    **Usages:**
        >>> exit, out, err = run_sync(cmd)
        >>> exit, out, err = run_sync(cmd, tee=True)
        >>> exit, out, err = run_sync(cmd, tee=True, log=(o, e))

    **Example:**
        >>> from pyxtern.xtern import run_sync

        >>> cmd = ["find", "./pyxtern", "-name", "*.py"]
        >>> exit, out, err = run_sync(cmd, tee=True)
        ./pyxtern/xtern.py
        ./pyxtern/__init__.py
        ./pyxtern/utils.py

    """
    # Read args and kwargs
    cmd = _check_cmd(cmd)
    dir = kwargs.get("dir", None)
    if dir:
        dir = op.abspath(dir)
    save = kwargs.get("save", None)
    timeout = kwargs.get("timeout", None)
    tee = kwargs.get("tee", False)
    outl, errl = kwargs.get("log", (None, None))

    with temporary_directory(dir=dir, save=save) as tmp:
        # Run command line
        proc = sp.Popen(cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        # Temporary files
        outf = op.join(tmp, "std.out")
        errf = op.join(tmp, "std.err")
        with open(outf, "wb") as stdout, open(errf, "wb") as stderr:
            outs = [stdout]
            errs = [stderr]
            # Add process streams
            if tee:
                outs.append(sys.stdout)
                errs.append(sys.stderr)
            # Add caller streams
            if outl:
                if isinstance(outl, list):
                    outs.extend(outl)
                else:
                    outs.append(outl)
            if errl:
                if isinstance(errl, list):
                    errs.extend(errl)
                else:
                    errs.append(errl)
            # Log to streams
            outt = _log_to_streams(proc.stdout, *outs)
            errt = _log_to_streams(proc.stderr, *errs)
            # Wait the end of the forwarding threads
            logs.info("Running command '{}'".format(" ".join(cmd)))
            try:
                outt.join()
                errt.join()
                proc.communicate(timeout=timeout)
            except (OSError, FileNotFoundError, sp.TimeoutExpired) as e:
                outt.join()
                errt.join()
                proc.kill()
                proc.communicate()
                raise e
        # Read stdout and stderr
        with open(outf, "rb") as f:
            stdo = f.read()
        stdo = stdo.decode("utf-8")
        with open(errf, "rb") as f:
            stde = f.read()
        stde = stde.decode("utf-8")
        # Handle command errors
        exit = proc.returncode
        if exit != 0:
            raise sp.CalledProcessError(exit, " ".join(cmd), stdo, stde)
    return exit, stdo, stde


class Runner(th.Thread):
    """
    Handles asynchronous external command.

    Keeps track of an asynchronous external command and stores its exit code,
    standard output and standard error.

    **Warning:**
        :class:`Runner` should not be used directly. Refer to the
            :func:`run_async` and :func:`run` functions for more information.

    **Usages:**
        >>> r = Runner(cmd, **kwargs)
        >>> r.start()
        >>> # Do some stuff.
        >>> exit, out, err = r.end()

    """

    def __init__(self, cmd, **kwargs):
        """
        **Args:**
            cmd (:obj:`list`): The external command to run.

            \**kwargs: Arguments that should be given to the :func:`run_async`
                function.

        **See also:**
            :func:`run_sync`
                For more arguments, refer to the :func:`run_sync` function.

        """
        super().__init__()
        self._cmd = cmd
        self._kwargs = kwargs
        self._exit = None
        self._out = ""
        self._err = ""

    @property
    def exit_code(self):
        """
        :obj:`int` | :obj:`None`: The exit code of the external function if
            it returns one, :obj:`None` otherwise.
        """
        return self._out

    @property
    def std_out(self):
        """
        :obj:`str`: The standard output of the external function.
        """
        return self.out

    @property
    def std_err(self):
        """
        :obj:`str`: The standard error of the external function.
        """
        return self.err

    def run(self):
        """
        Run an external command asynchronously.

        Run an external command asynchronously and stores its exit code,
        standard output and standard error.

        """
        self._exit, self._out, self._err = run_sync(self._cmd, **self._kwargs)

    def end(self):
        """
        Return the exit code of the external command and its standard
        output and standard error.

        Waits for the external command to complete and return its exit code,
        standard output and standard error.

        **Returns:**
            :obj:`int` | :obj:`None`: The :func:`exit_code`.

            :obj:`str`: The :func:`std_out`.

            :obj:`str`: The :func:`std_err`.

        """
        self.join()
        return self.exit, self.out, self.err


def run_async(cmd, **kwargs):
    """
    Run an external commad asynchronously.

    Run an external command asynchronously and return a :class:`Runner`
    instance to keep track of it.

    **Args:**
        cmd (:obj:`list`): The list formatted command to run.

        \**kwargs: Arguments that should be given to the :func:`run_sync`
            function.

    **See also:**
        :func:`run_sync`

    **Returns:**
        :obj:`Runner`: The :class:`Runner` instance corresponding to the
            external command.

    **Usages:**
        >>> r = run_async(cmd, **kwargs)
        >>> # Do some stuff.
        >>> exit, out, err = r.end()

    """
    runner = Runner(cmd, **kwargs)
    runner.start()
    return runner


def run(cmd, **kwargs):
    """
    Run an external command.

    Run an external command and return either its exit code, standard output
    and standard error if synchronous or a :class:`Runner` instance if
    asynchronous.

    **Args:**
        cmd (:obj:`list`): The list formatted command to run.

        sync (:obj:`bool`): :obj:`True` if the external command should be ran
            synchronously (default). :obj:`False` if it should be ran
            asynchronously.

        \**kwargs: Arguments that should be given to the :func:`run_sync`
            function.

    **See also:**
        :func:`run_sync`
            For more arguments, refer to the :func:`run_sync` function.

    **Returns:**
        Synchrous
            Refer to :func:`run_sync` function for return values.

        Asynchronous
            Refer to :func:`run_async` function for return values.

    **Usages:**
        >>> exit, out, err = run(cmd, **kwargs)
        >>> exit, out, err = run(cmd, sync=True, **kwargs)

        >>> r = run(cmd, sync=False, **kwargs)
        >>> # Do some stuff
        >>> exit, out, err = r.end()

    """
    sync = kwargs.pop("sync", True)
    if sync:
        return run_sync(cmd, **kwargs)
    else:
        return run_async(cmd, **kwargs)


def xtern(func):
    """
    Allow user to run commands produced by functions.

    This decorator can be used to automaticaly run external commands produced
    by the decorated function.

    **Args:**
        func(:obj:`callable`): The decorated function. It should return a list
            formatted command.

    **See also:**
        :func:`run`
            The decorated function accepts all the arguments of the :func:`run`
            function and returns the same values.

    **Usages:**
        >>> @xtern
        >>> def foo(*args, **kwargs):
        >>>     return cmd

        >>> exit, out, err = foo(*args, **kwargs)
        >>> exit, out, err = foo(*args, sync=True, **kwargs)

        >>> foo_r = foo(*arg, sync=False, **kwargs)
        >>> # Do some stuff
        >>> exit, out, err = foo_r.end()

    **Example:**
        >>> from pyxtern import xtern

        >>> @xtern
        >>> def find_ext(*args, **kwargs):
        >>>     cmd = ["find",
        >>>            "./pyxtern",
        >>>            "-name",
        >>>            "*.{}".format(kwargs.pop("ext", "txt"))]
        >>>     return cmd

        >>> exit, out, err = find_ext(tee=True)

        >>> exit, out, err = find_ext(ext="py", tee=True)
        ./pyxtern/xtern.py
        ./pyxtern/__init__.py
        ./pyxtern/utils.py

    """
    @ft.wraps(func)
    def wrapper(*args, **kwargs):
        cmd = func(*args, **kwargs)
        return run(cmd, **kwargs)
    return wrapper
