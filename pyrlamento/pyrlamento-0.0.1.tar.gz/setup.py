import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pyrlamento",
    version="0.0.1",
    author="Cláudio Pereira",
    author_email="development@claudiop.com",
    description="Generic interface to legal systems",
    license="GPL V3",
    keywords="law, interface, wrapper",
    url="https://gitlab.com/claudiop/pyrlamento",
    packages=find_packages(),
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Text Processing :: Markup :: HTML",
    ], install_requires=['requests', 'beautifulsoup4']
)
