# Copyright (c) 2019 bluelief.
# This source code is licensed under the MIT license.

import platform
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rapidrush.utils.version import (
    git_commit_count,
    git_commit_date,
    git_commit_hash,
    git_describe,
)

result = "rapidrush %s %s @ %s-%s %s\n"
result += "commit: %s release: %s\n"
result = result % (
    __import__("rapidrush").__version__,
    git_commit_count(),
    platform.system(),
    platform.machine(),
    git_describe(),
    git_commit_hash(),
    git_commit_date(),
)

print(result)
