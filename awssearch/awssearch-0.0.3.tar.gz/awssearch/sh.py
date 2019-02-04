import os
import subprocess
import logging


def clean(stream):
    try:
        return [line.decode("utf-8").replace('\n', '') for line in stream]
    except UnicodeDecodeError:
        return [line.decode("ISO-8859-1").replace('\n', '') for line in stream]


def sh(command, stdin=None):
    """
    Executa um comando via ssh passando stdin como entrada do comando
    :param command: comando
    :param stdin: entrada
    :return: saída do comando
    """
    if stdin:
        read, write = os.pipe()
        os.write(write, stdin.encode())
        os.close(write)
    else:
        read = None

    process = subprocess.Popen(
        command,
        shell=True,
        stdin=read,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    output = process.stdout.readlines()
    error = process.stderr.readlines()

    output = clean(output)
    error = clean(error)
    result = output + error

    # loglevel = logging.info if not len(error) else logging.warning
    loglevel = logging.info
    loglevel(
        "command = `%s`\n"
        "output = '%s'"
        % (command, result)
    )

    return output + error
