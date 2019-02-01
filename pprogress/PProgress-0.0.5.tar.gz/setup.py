from distutils.core import setup
import setuptools

setup(
    name='PProgress',
    version='0.0.5',
    author="Fergus Horrobin",
    author_email="fergus.horrobin@mail.utoronto.ca",
    description="Simple Python progress bar for parallel programs.",
    packages=['pprogress',],
    license='GPL',
    long_description=open('README.rst').read(),
)
