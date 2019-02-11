try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # python 2 backport


def makedirs(path, exist_ok=False):
    Path(path).mkdir(parents=True, exist_ok=exist_ok)


def path_for(*parts):
    return Path(*parts)


def ensure_count_is_valid(count):
    count = int(count)
    if count <= 0:
        raise ValueError("`count` should be a positive integer")
