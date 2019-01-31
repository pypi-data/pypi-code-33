from setuptools import setup
from os import path

author = 'bnbdr'
setup(
    name='wyfy',
    version='0.1',
    author=author,
    author_email='bad.32@outlook.com',
    description="print wifi passwords (windows only)",
    url='https://github.com/{}/wyfy'.format(author),
    license='MIT',
    long_description=open(path.join(path.abspath(path.dirname(__file__)), 'README.md')).read(),
    long_description_content_type='text/markdown',
    keywords='wifi',
    packages=['wyfy'],
    entry_points = {
        'console_scripts': ['wyfy=wyfy.wyfy:main'],
    },
    classifiers=(
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ),
)
