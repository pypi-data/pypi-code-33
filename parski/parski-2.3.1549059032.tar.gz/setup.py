from setuptools import setup, find_packages

setup(
    description="Python Library for searching json lists.",
    author="Barry Howard",
    author_email="barry.howard@ge.com",
    url="https://github.build.ge.com/Cloudpod/parski",
    version="2.3.1549059032",
    keywords=[u'json', u'filter', u'ge', u'cloudops', u'aws'],
    long_description="Python Library for searching json lists.",
    name="parski",
    packages=find_packages(exclude=["build", "build/*"])
)
