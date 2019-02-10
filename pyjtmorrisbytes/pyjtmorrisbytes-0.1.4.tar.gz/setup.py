#!/usr/bin/env python
from setuptools import setup, find_packages
import os


env = os.environ.get("DO_COMPILE",False)
travis= os.environ.get("TRAVIS",False)
do_compile = env == 'true' or travis =="true"

print(env)
print(travis)
print(do_compile)

if do_compile is True:
    print("dev or testing detected. importing cython")
    from Cython.Build import cythonize
    from setuptools import Extension


if __name__ == "__main__":
    if do_compile is True:
        print("compiliation has been requested")
        extensions = [
            Extension('pyjtmorrisbytes.*', [os.path.join("src", 'pyjtmorrisbytes', '*.pyx')]),
            Extension('pyjtmorrisbytes.models.*', [os.path.join('src', 'pyjtmorrisbytes', 'models', '*.pyx')]),
            Extension('pyjtmorrisbytes.factories.*', [os.path.join('src', 'pyjtmorrisbytes', 'factories', '*.pyx')]),
            Extension('pyjtmorrisbytes.views.*', [os.path.join('src', 'pyjtmorrisbytes', 'views', '*.pyx')]),
            Extension('pyjtmorrisbytes.controllers.*', [os.path.join('src', 'pyjtmorrisbytes', 'controllers', '*.pyx')]),
            Extension('pyjtmorrisbytes.config.*', [os.path.join('src', 'pyjtmorrisbytes', 'config', '*.pyx')]),
        ]

        setup(
            name="pyjtmorrisbytes",
            versioning='branch(master,dev, fix-travis):dev',
            setup_requires=['setupmeta', 'pytest-runner', 'pytest-cython'],
            ext_modules=cythonize(extensions, language_level=3)
        )
    else:
        setup(
            name="pyjtmorrisbytes",
            versioning='branch(master,dev, fix-travis):dev',
            setup_requires=['setupmeta', 'pytest-runner', 'pytest-cython'],
        )

