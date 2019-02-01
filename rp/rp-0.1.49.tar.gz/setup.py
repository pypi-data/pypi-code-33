from setuptools import setup,find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path
from rp import *
here=path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here,'README'),encoding='utf-8') as f:
    long_description=f.read()

setup   (
        name='rp',
        # Versions should comply with PEP440.  For a discussion on single-sourcing
        # the version across setup.py and the project code, see
        # http://packaging.python.org/en/latest/tutorial.html#version
        version='0.1.49',
        description='Ryan\'s Python',
        url='https://github.com/RyannDaGreat/Quick-Python',
        author='Ryan Burgert',
        author_email='ryancentralorg@gmail.com',
        # license='Maybe MIT? trololol no licence 4 u! (until i understand what *exactly* it means to have one)',
        keywords='not_searchable_yet_go_away_until_later_when_this_is_polished',
        packages=["rp",'rp.rp_ptpython','rp.prompt_toolkit',
                  "rp.prompt_toolkit.clipboard",
                  "rp.prompt_toolkit.contrib",
                  "rp.prompt_toolkit.contrib.completers",
                  "rp.prompt_toolkit.contrib.regular_languages",
                  "rp.prompt_toolkit.contrib.telnet",
                  "rp.prompt_toolkit.contrib.validators",
                  "rp.prompt_toolkit.eventloop",
                  "rp.prompt_toolkit.filters",
                  "rp.prompt_toolkit.key_binding",
                  "rp.prompt_toolkit.key_binding.bindings",
                  "rp.prompt_toolkit.layout",
                  "rp.prompt_toolkit.styles",
                  "rp.prompt_toolkit.terminal",
                  ]
        ,
        install_requires=['wcwidth','pygments',"ptpython","ipython","psutil","doge"],
        entry_points=
        {
            'console_scripts':['rp = rp.__main__:main']
        },
    )




