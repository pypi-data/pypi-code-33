# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
from datetime import date

__all__ = [
    "__version__",
    "__description__",
    "__keywords__",
    "__author__",
    "__author_email__",
    "__url__",
    "__platforms__",
    "__license__",
    "__classifiers__",
    "__install_requires__",
    "__zip_safe__",
    "__copyright__",
]

__version__ = '3.1.4'
__description__ = "nimbus_scrapy"
__keywords__ = ["nimbus_scrapy", "nimbus", "scrapy"]
__author__ = "william"
__author_email__ = "william.ren@live.cn"
__maintainer__ = "william"
__maintainer_email__ = "william.ren@live.cn"
__url__ = "https://github.com/williamren"
__platforms__ = "Any"
__license__ = "Apache License 2.0"
__classifiers__ = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Topic :: Internet :: WWW/HTTP",
    "Environment :: Web Environment",
    "Framework :: Django",
    "Framework :: Django :: 1.8",
    "Framework :: Django :: 1.9",
    "Framework :: Django :: 1.10",
    "Framework :: Django :: 1.11",
]
__install_requires__ = [
    "Scrapy>=1.0.0",
    "SQLAlchemy>=1.0.0",
    "selenium>=3.0.0",
    "redis>=2.0.0",
    "pymongo>=3.0.0",
    "dateutils>=0.6.6",
    "python-dateutil>=2.6.1",
    "beautifulsoup4>=4.3.1",
    "zhon>=1.1.5",
    "nimbus_utils>=0.3.1",
    "Pillow>=5.0.0",
    "crochet>=1.9.0",
    "six",
]
__zip_safe__ = False
__copyright__ = "Copyright 2001-{0} {1}".format(date.today().year, __author__)


