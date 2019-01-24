"""

Code based on `setuptools-git-version` which can be found here:

    https://github.com/pyfidelity/setuptools-git-version

"""

from pkg_resources import get_distribution
from subprocess import check_output, CalledProcessError, STDOUT


command = 'git describe --tags --long --dirty'
fmt = '{tag}.{commitcount}+{gitsha}'


def format_version(version, fmt=fmt):
    parts = version.split('-')
    assert len(parts) in (3, 4)
    dirty = len(parts) == 4
    tag, count, sha = parts[:3]
    if count == '0' and not dirty:
        return tag
    return fmt.format(tag=tag, commitcount=count, gitsha=sha.lstrip('g'))


def get_version():

    try:
        version = check_output(command.split(), stderr=STDOUT).decode('utf-8')
        version = version.strip()
        version = format_version(version=version)

    except:
        version = get_distribution("f2-probe-detector").version

    return version


# determine version from git
__version__ = get_version()
