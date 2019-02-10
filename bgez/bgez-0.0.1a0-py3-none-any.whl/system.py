import sys
import os
import re

from glob import iglob
from pathlib import Path
from platform import system

__all__ = [
    'is_windows',
    'is_linux',
    'is_mac',
    'is_blender',
    'is_upbge',
    'is_game',
    'project',
]

is_windows = system() == 'Windows'
is_linux = system() == 'Linux'
is_mac = system() == 'Darwin'

def get_python_exe():
    if is_windows or is_linux:
        python_path = Path(sys.base_prefix) / 'bin' / 'python*'
        name_test = re.compile(r'python(\d(.\d\w?)?)?$')

        for path in iglob(str(python_path)):
            if name_test.search(path):
                return path

    return sys.executable
python = get_python_exe()

try:
    from bpy import app
    is_upbge = getattr(app, 'upbge_version', None) is not None
    is_blender = is_upbge or getattr(app, 'version', None) is not None
except ImportError:
    is_blender = False
    is_upbge = False

try:
    from bge import app, logic, types, texture, events, constraints
    project = logic.expandPath('//')
    del app, logic, types, texture, events, constraints
    is_game = True
except ImportError:
    project = os.getcwd()
    is_game = False
