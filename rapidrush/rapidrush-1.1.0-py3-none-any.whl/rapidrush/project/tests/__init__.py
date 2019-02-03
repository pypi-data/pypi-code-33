SOURCEHEADER

import platform
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PACKAGENAME.utils.version import (
    git_commit_count,
    git_commit_date,
    git_commit_hash,
    git_describe,
)

result = "PACKAGENAME %s %s @ %s-%s %s\n"
result += "commit: %s release: %s\n"
result = result % (
    __import__("PACKAGENAME").__version__,
    git_commit_count(),
    platform.system(),
    platform.machine(),
    git_describe(),
    git_commit_hash(),
    git_commit_date(),
)

print(result)
