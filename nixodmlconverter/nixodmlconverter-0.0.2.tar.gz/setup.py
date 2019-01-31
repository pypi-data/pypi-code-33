import json
import sys
from io import open
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("info.json") as infofile:
    infodict = json.load(infofile)

VERSION = infodict["VERSION"]
FORMAT_VERSION = infodict["FORMAT_VERSION"]
AUTHOR = infodict["AUTHOR"]
COPYRIGHT = infodict["COPYRIGHT"]
CONTACT = infodict["CONTACT"]
HOMEPAGE = infodict["HOMEPAGE"]
CLASSIFIERS = infodict["CLASSIFIERS"]


packages = ['nixodmlconverter']

with open('README.md', encoding="utf8") as f:
    description_text = f.read()

install_req = ["odML", "nixio>=1.5.0b1"]

if sys.version_info < (3, 4):
    install_req += ["enum34"]

setup(
    name='nixodmlconverter',
    version=VERSION,
    description='Converter between NIX and odML format',
    author=AUTHOR,
    author_email=CONTACT,
    url=HOMEPAGE,
    packages=packages,
    test_suite='test',
    install_requires=install_req,
    include_package_data=True,
    long_description=description_text,
    long_description_content_type="text/markdown",
    classifiers=CLASSIFIERS,
    license="BSD"
)
