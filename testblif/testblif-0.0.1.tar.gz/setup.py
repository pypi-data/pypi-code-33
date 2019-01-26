from setuptools import setup

import re

version = re.search(
    '^__version__ *= *"(.*)".*$',
    open('testblif/testblif.py').read(),
    re.M
).group(1)

with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

with open("requirements.txt","r") as f:
    req = f.readlines()

setup(
    name = "testblif",
    packages = ['testblif'],
    entry_points = {
        'console_scripts': ['testblif = testblif.testblif:main']
    },
    version=version,
    description = "Unit-testing-style for .blif files for SIS. Main website: https://ptolemy.berkeley.edu/projects/embedded/pubs/downloads/sis/",
    long_desc = long_descr,
    author = "Cesare Montresor",
    author_email = "cesare.montresor@gmail.com",
    url = "https://github.com/cesare-montresor/test-blif",
    install_requires=req
)