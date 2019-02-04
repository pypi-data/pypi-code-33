from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.install import install
from setuptools.command.egg_info import egg_info
import os
import distutils.cmd
import distutils.log
import subprocess
import sys


def find_stubs(package):
    stubs = []
    for root, dirs, files in os.walk(package):
        for file in files:
            path = os.path.join(root, file).replace(package + os.sep, '', 1)
            stubs.append(path)
    return {package: stubs}


class GenerateStubsCommand(distutils.cmd.Command):
    description = 'run generate_stubs for pyxmolpp2'

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.announce(
            'Running command: pybind11_stubgen.py',
            level=distutils.log.INFO)
        subprocess.call([sys.executable,
                         os.path.join(os.path.dirname(__file__), "external", "pybind11-stubgen",
                                      "pybind11_stubgen.py"),
                         "--output-dir", os.path.dirname(os.path.abspath(__file__)),
                         "--no-setup-py",
                         "pyxmolpp2"
                         ])



def generate_stubs_before(command):
    class Generate_stubs_first(command):
        def run(self):
            self.run_command("generate_stubs")
            return command.run(self)
    return Generate_stubs_first


setup(
    name='pyxmolpp2-stubs',
    maintainer="Sergei Izmailov",
    maintainer_email="sergei.a.izmailov@gmail.com",
    description="PEP 561 type stubs for pyxmolpp2",
    url="https://github.com/sizmailov/pyxmolpp2",
    version="0.0.2",
    packages=['pyxmolpp2-stubs'],
    cmdclass={
        'generate_stubs': GenerateStubsCommand,
        'install': generate_stubs_before(install),
        'egg_info': generate_stubs_before(egg_info),
        'build_py': generate_stubs_before(build_py)
    },
    # PEP 561 requires these
    install_requires=['pyxmolpp2'],
    package_data=find_stubs('pyxmolpp2-stubs')
)
