import sys
import webbrowser
import functools
import operator
from distutils.core import setup

name = 'ensure-no-deps'
version = '0.0.0'
url = 'https://pip.pypa.io/en/stable/reference/pip_install/#cmdoption-no-deps'
message = (
    'You just attempted to install a package that depends on ensure-no-deps, '
    'that package must be installed with `pip install --no-deps` see also: ' +
    url
)


argv = functools.partial(operator.contains, set(sys.argv))


if (argv('install') or  # pip install ..
        (argv('--dist-dir') and argv('bdist_egg'))):  # easy_install
    webbrowser.open_new(url)
    raise Exception(message)


if argv('bdist_wheel'):  # modern pip install
    raise Exception(message)


setup(
    name=name,
    version=version,
    maintainer='Thomas Grainger',
    maintainer_email=name + '@graingert.co.uk',
    long_description=message,
    url=url,
)
