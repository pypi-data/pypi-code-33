import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = '0.3.0'

setup(
    name='dytodo',
    version=version,
    description="todo",
    long_description=README,
    classifiers=[
    ],
    keywords='pytodo',
    author='me',
    author_email='me@example.org',
    url='https://example.org',
    license='LGPL v3',
    py_modules=['todo'],
    include_package_data=True,
    install_requires=[
        'click',
        'dyools',
        'terminaltables',
        'colorclass',
        'pyaml',
        'dateparser',
    ],
    entry_points='''
        [console_scripts]
        todo=todo:maintodo
        sign=todo:mainsign
    ''',
)
