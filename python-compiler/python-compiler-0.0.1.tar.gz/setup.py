import sys
from setuptools import setup


if sys.version_info < (3, 0):
    sys.stderr.write("Sorry, Python < 3.0 is not supported\n")
    sys.exit(1)


setup(name='python-compiler',
      version='0.0.1',
      description="""Python bytecode compiler written in Python""",
#      long_description=open('README.rst').read(),
      url='https://github.com/pfalcon/python-compiler',
      author='Python Developers',
      maintainer='Paul Sokolovsky',
      author_email='pfalcon@users.sourceforge.net',
      license='Python',
      packages=['compiler'])
