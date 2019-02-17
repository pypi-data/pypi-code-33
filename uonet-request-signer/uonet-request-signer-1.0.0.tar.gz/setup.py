# -*- coding: utf-8 -*-

from setuptools import setup
from os import path
import io
import re

here = path.abspath(path.dirname(__file__))

with io.open(path.join(here, "README.md"), "rt", encoding="utf8") as f:
    long_description = f.read()

with io.open(
    path.join(here, "uonet-request-signer/__init__.py"), "rt", encoding="utf8"
) as f:
    version = re.search(r"__version__ = \"(.*?)\"", f.read()).group(1)

setup(
    name="uonet-request-signer",
    version=version,
    description="Uonet+ request signer for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wulkanowy/uonet-request-signer",
    author="Wulkanowy",
    author_email="wulkanowyinc@gmail.com",
    maintainer="Kacper Ziubryniewicz",
    maintainer_email="kapi2289@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Security :: Cryptography",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=["uonet_request_signer"],
    package_dir={"uonet_request_signer": "uonet-request-signer"},
    install_requires=["pyopenssl"],
    extras_require={"testing": ["pytest"]},
)
