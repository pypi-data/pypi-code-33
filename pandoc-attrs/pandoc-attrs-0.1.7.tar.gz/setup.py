from setuptools import setup
import io
from os import path as p

try:
    with io.open(p.join(p.dirname(p.abspath(__file__)), 'README.md'),
                 encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    long_description = ''

setup(
    name="pandoc-attrs",
    version='0.1.7',
    description="An Attribute class to be used with pandocfilters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=['pandocattrs'],
    include_package_data=True,
    author="Aaron O'Leary",
    author_email='dev@aaren.me',
    license='BSD 2-Clause',
    url='http://github.com/kiwi0fruit/pandoc-attrs',
    install_requires=['pandocfilters', ],
)
