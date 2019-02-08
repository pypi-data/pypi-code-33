#!/usr/bin/env python


__title__ = 'pyjtmorrisbytes'

try:
    from src.pyjtmorrisbytes import __title__
except:
    try:
        from pyjtmorrisbytes import __title__
    except:
        pass
    
try:
    from src.app import __title__
except:
    try:
        from app import __title__
    except:
        pass

from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize
import setuptools.command.test
import os.path
try:
    from sphinx.setup_command import BuildDoc

    cmdclass = {'build_sphinx': BuildDoc}
except:
    cmdclass = {'build_sphinx': object}
#compiler options
from Cython.Compiler import Options
Options.docstrings = True
Options.annotate=True


rootdir = os.path.abspath(os.path.join('.', 'src'))
extensions = [
    Extension('pyjtmorrisbytes.*', [os.path.join("src", 'pyjtmorrisbytes', '*.pyx')]),
    Extension('pyjtmorrisbytes.models.*', [os.path.join('src', 'pyjtmorrisbytes', 'models', '*.pyx')]),
    Extension('pyjtmorrisbytes.factories.*', [os.path.join('src', 'pyjtmorrisbytes', 'factories', '*.pyx')]),
    Extension('pyjtmorrisbytes.views.*', [os.path.join('src', 'pyjtmorrisbytes', 'views', '*.pyx')]),
    Extension('pyjtmorrisbytes.controllers.*', [os.path.join('src', 'pyjtmorrisbytes', 'controllers', '*.pyx')]),
    Extension('pyjtmorrisbytes.config.*', [os.path.join('src', 'pyjtmorrisbytes', 'config', '*.pyx')]),

    # Extension('sqlalchemy.*', [os.path.join(rootdir, 'sqlalchemy', '**',   '*.py')]),
]
if __name__ == "__main__":    
    setup(
        # description='my library files commonly used with my apps ',
        # license=license,
        # packages=find_packages(exclude='test*'),
        version='0.1.5',
        cmdclass=cmdclass,
        package_data={'pyjtmorrisbytes': ['*.pxd', '*.py']},
        include_package_data=True,
        # test_suite='setup.setup_test_suite',
        zip_safe=False,
        ext_modules=cythonize(extensions,
                            language_level=2,
                            exclude=['**init**',
                                     'init'
                                     '__init__',
                                     'compat'],
                            # exclude_failures=True
                            annotate=True
                            ),
                            
        setup_requires=['pytest-runner', 'cython', 'setupmeta', 'tox-setuptools', 'sphinx'],
        entry_points={'console_scripts': ['pyjtmorrisbytes= pyjtmorrisbytes.__init__:main'],
                      'setuptools.installations': 
                        ['eggsecutable = pyjtmorrisbytes.__init__:main_func']
         },

        tests_require=['pytest']
    )
