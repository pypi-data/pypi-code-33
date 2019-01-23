import subprocess
from tempfile import NamedTemporaryFile
from pathlib import Path
import shutil
import os

PYTHON_VERSION = (3, 6, 5)

COMMANDS = [['sensible-editor'], ['open', '-W']]


def editor(arg):
    with NamedTemporaryFile() as tempfile:
        Path(tempfile.name).write_text(arg)
        command = [os.environ.get('EDITOR')]
        if not command[0]:
            iterator = (c for c in COMMANDS if shutil.which(c[0]))
            command = next(filter(None, iterator), None)
            if not command:
                raise RuntimeError("The manage command required an editor")
        subprocess.run(command + [tempfile.name])
        return Path(tempfile.name).read_text()
