import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    raise Exception("Python 3.6 or higher is required. Your version is %s." % sys.version)

long_description = open('README.rst').read()

__version__ = ""
exec(open('telemetry_1a23/__version__.py').read())

setup(
    name='1a23-telemetry',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    version=__version__,
    description='1A23 Telemetry Toolkit',
    long_description=long_description,
    author='Eana Hufwe',
    author_email='ilove@1a23.com',
    url='https://github.com/blueset/1a23-telemetry',
    license='AGPLv3+',
    python_requires='>=3.6',
    include_package_data=True,
    keywords=['1A23 Studio', 'Telemetry'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities"
    ],
    install_requires=[
        "requests",
        "sentry_sdk==0.6.9",
        "logzio-python-handler",
        "logdna",
        "typing",
        "typing_extensions"
    ]
)
