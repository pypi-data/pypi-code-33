"""
:mod:`pyxtern.utils` provides the :func:`temporary_directory` function.

"""
import contextlib as cl
import logging as lg
import os
import os.path as op
import shutil as su
import tempfile as tf
import threading as th

log = lg.getLogger(__name__)


def _init_temporary_directory(dir=None, save=None):
    if dir:
        os.makedirs(op.abspath(dir), exist_ok=True)
    tmp = tf.mkdtemp(dir=dir)
    log.debug("Created temporary directory at: '{}'".format(tmp))
    cwd = os.getcwd()
    if save:
        save = op.abspath(save)
    return tmp, cwd, save


def _end_temporary_directory(tmp, cwd, save=None):
    if save:
        os.makedirs(save, exist_ok=True)
        for f in os.listdir(tmp):
            su.move(op.join(tmp, f), save)
        log.info("Saved result at: '{}'".format(save))
    os.chdir(cwd)
    log.debug("Moved to previous working directory at: '{}'".format(cwd))
    su.rmtree(tmp)
    log.debug("Removed temporary directory at: '{}'".format(tmp))


@cl.contextmanager
def temporary_directory(dir=None, save=None):
    """
    Creates a temporary context deleted after use.

    This context creates a temporary directory, moves the working directory
    in it, proceeds and then exits and removes the folder.

    **Args:**
        dir (:obj:`str`): The path where to create the temporary directory. If
            set to :obj:`None`, the system default temporary location is used.
            For more information, refer to :func:`mkdtemp() <tempfile.mkdtemp>`
            documentation.

        save (:obj:`str`): The path were to save the content of the temporary
            directory before deleting it. If :obj:`None`, the content of the
            temporary directory is not saved.

    **Usages:**
        >>> with temporary_directory():
        >>> with temporary_directory() as tmp:
        >>> with temporary_directory(dir="./tmp"):
        >>> with temporary_directory(save=./res):
        >>> with temporary_directory(dir="./tmp", save="./res"):

    """
    # Create the temporary directory
    tmp, cwd, save = _init_temporary_directory(dir, save)
    # Move to the temporary directory
    try:
        os.chdir(tmp)
        log.debug("Moved to temporary directory at: '{}'".format(tmp))
        yield tmp
    # Move back to cwd and remove temporary directory
    finally:
        _end_temporary_directory(tmp, cwd, save)


def _log_to_streams(ins, *outs):
    """This function allows a stream to be forwarded to multiple other ones.

    :arg ins:  The input stream.
    :arg outs: The output streams.

    :returns:  The forwarding thread.
    """
    # Check if each stream is a file-like object
    outm = [getattr(o, "mode", "w") for o in outs]

    # Function to forward input to output stream
    def forward():
        for l in iter(ins.readline, b""):
            for i, o in enumerate(outs):
                if "b" in outm[i]:
                    o.write(l)
                else:
                    o.write(l.decode("utf-8"))

    # Create the forwarding threads
    t = th.Thread(target=forward)
    t.daemon = True
    t.start()
    log.debug("Started forwarding thread")
    return t


def _check_cmd(cmd):
    """This functions checks wether cmd is a list of strings or not. If not, it
    tries to convert it.

    :arg cmd: The command to check.

    :returns: The formatted list of strings.
    """
    log.debug("Received command '{}'".format(cmd))
    if isinstance(cmd, str):
        cmd = cmd.split()
    elif isinstance(cmd, list):
        for i, s in enumerate(cmd):
            if not isinstance(s, str):
                cmd[i] = str(s)
    log.debug("Converted command to '{}'".format(cmd))
    return cmd
