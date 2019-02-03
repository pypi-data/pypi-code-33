from dask.core import get_dependencies


def get_all_dependencies(dsk, key):
    """
    Get dependencies recursively
    """
    deps = []
    for d in get_dependencies(dsk, key):
            deps.append(d)
            deps.extend(get_all_dependencies(dsk, d))
    return deps
