import setuptools
from distutils.util import convert_path

# The following is used so we can set the version in one place (version.py) for use in both openfin_log_cli.py and
# in setup.py (without needing setup.py to depend on something from inside the package).
# https://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
main_ns = {}
ver_path = convert_path('log_manager_cli/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as requirements_file:
    required = requirements_file.read().splitlines()

setuptools.setup(
    name='oflog',
    version=main_ns['__version__'],
    author='OpenFin',
    author_email='dev@openfin.co',
    description='CLI for the OpenFin Log Management Service',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/openfin/log-manager-cli',
    install_requires=required,
    packages=setuptools.find_packages(),
    classifiers=(
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: Apache Software License'
    ),
    entry_points={
        'console_scripts': ['oflog=log_manager_cli.openfin_log_cli:main']
    }
)
