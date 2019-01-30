#!/usr/bin/env python
"""
 Copyright (C) 2016 by SolarWinds, LLC.
 All rights reserved.
"""

import sys
import os
from distutils import log
from distutils.command.build import build
from setuptools import setup, Extension
from setuptools.command.install import install
from setuptools.command.sdist import sdist
from setuptools.command.build_ext import build_ext

version = '3.4.8'

def is_alpine_distro():
    # checking alpine dist
    if os.path.exists("/etc/alpine-release"):
        return True

    try:
        with open("/etc/os-release", 'r') as osr:
            releases = osr.readlines()
            releases = [ l[:-1] for l in releases ]
        if 'NAME="Alpine Linux"' in releases:
            return True
    except Exception:
        pass

    return False

is_alpine = is_alpine_distro()
is_darwin = sys.platform == 'darwin'

def python_version_supported():
    if sys.version_info[0] == 2:
        if sys.version_info[1] not in (7,):
            return False
    elif sys.version_info[0] == 3:
        if sys.version_info[1] < 4:
            return False
    return True

def choose_oboe():
    log.info("[SETUP] choose to link to platform specific liboboe")

    liboboe = "liboboe-1.0-x86_64.so.0.0.0"
    alpineoboe = "liboboe-1.0-alpine-x86_64.so.0.0.0"
    tmp_oboe= "/".join(["./appoptics_apm/swig",  liboboe])
    tmp_alpine = "/".join(["./appoptics_apm/swig",  alpineoboe])

    # choose platform compatible oboe and rename it to default name
    try:
        if is_alpine:
            if os.path.exists(tmp_oboe):
                os.remove(tmp_oboe)
            if os.path.exists(tmp_alpine):
                os.renames(tmp_alpine, tmp_oboe)
        elif is_darwin:
            if os.path.exists(tmp_oboe):
                os.remove(tmp_oboe)
            if os.path.exists(tmp_alpine):
                os.remove(tmp_alpine)
        else:
            # assume all others are g-libc compatible
            if os.path.exists(tmp_alpine):
                os.remove(tmp_alpine)

        # liboboe should have been removed for darwin, create symlink for others
        if os.path.exists(tmp_oboe):
            os.symlink(liboboe, "./appoptics_apm/swig/liboboe-1.0.so")
            os.symlink(liboboe, "./appoptics_apm/swig/liboboe-1.0.so.0")
    except Exception  as ecp:
        log.info("[SETUP] failed to set up platform specific oboe... {e}".format(e=ecp))

def os_supported():
    return sys.platform.startswith('linux')


if not (python_version_supported() and os_supported()):
    log.warn("[SETUP] This package supports only Python 2.7, 3.3 and above on Linux"
             "Other platform or python versions may not work as expected.")

ext_modules = [Extension('appoptics_apm.swig._oboe',
                         sources=['appoptics_apm/swig/oboe_wrap.cxx'],
                         depends=['appoptics_apm/swig/oboe.hpp'],
                         include_dirs=['appoptics_apm/swig', 'appoptics_apm'],
                         libraries=['oboe-1.0', 'rt'],
                         library_dirs=['appoptics_apm/swig'],
                         runtime_library_dirs=['$ORIGIN']), ]

class CustomBuild(build):
    def run(self):
        choose_oboe()
        self.run_command('build_ext')
        build.run(self)

class CustomBuildExt(build_ext):
    def run(self):
        if is_darwin:
            return
        build_ext.run(self)

class CustomInstall(install):
    def run(self):
        install.run(self)

class CustomSdist(sdist):
    def run(self):
        log.info("remove liboboe links...")
        os.remove("./appoptics_apm/swig/liboboe-1.0.so")
        os.remove("./appoptics_apm/swig/liboboe-1.0.so.0")
        sdist.run(self)

try:
    import pypandoc
    rst_long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    # fail "gracefully"
    rst_long_description = open('README.md').read()

setup(name='appoptics_apm',
      cmdclass={'build': CustomBuild, 'build_ext': CustomBuildExt, 'install': CustomInstall, 'sdist': CustomSdist},
      version=version,
      author='SolarWinds, LLC',
      author_email='support@appoptics.com',
      url='https://www.appoptics.com/monitor/python-performance',
      download_url='https://pypi.python.org/pypi/appoptics_apm',
      description='AppOptics APM libraries, instrumentation, and web middleware components '
                  'for WSGI, Django, and Tornado.',
      long_description=rst_long_description,
      keywords='appoptics_apm traceview tracelytics oboe liboboe instrumentation performance wsgi middleware django',
      ext_modules=ext_modules,
      packages=['appoptics_apm', 'appoptics_apm.swig'],
      package_data={'appoptics_apm': ['swig/liboboe-1.0.so.0', 'swig/VERSION',
          'swig/bson/bson.h', 'swig/bson/platform_hacks.h']},
      license='LICENSE.txt',
      install_requires=['decorator', 'six'])
