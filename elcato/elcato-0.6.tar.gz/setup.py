# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages


LICENSE_PATH = os.path.join(os.path.dirname(__file__), "LICENSE")
README_PATH = os.path.join(os.path.dirname(__file__), "readme.org")
VERSION_PATH = os.path.join(os.path.dirname(__file__), "elcato", "version.py")
version = {}

with open(VERSION_PATH) as fp:
    exec(fp.read(), version)

with open(README_PATH) as f:
    readme = f.read()

with open(LICENSE_PATH) as f:
    license = f.read()

setup(
    name="elcato",
    version=version["__version__"],
    description="Static blog generator",
    long_description=readme,
    author="Oliver Marks",
    author_email="oly@digitaloctave.com",
    entry_points={"console_scripts": ["elcato=elcato.__init__:main"]},
    url="https://gitlab.com/python-open-source-library-collection/elcato",
    license=license,
    include_package_data=True,
    packages=find_packages(exclude=("tests", "docs")),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GPL-3 License",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
        "Topic :: Text Processing :: Filters",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    install_requires=[
        "python-dotenv",
        "pyyaml",
        "feedgen",
        "pygments",
        "eorg",
        "enaml-web",
        "jinja2",
        "pillow",
        "css-html-js-minify",
        "python-slugify",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
