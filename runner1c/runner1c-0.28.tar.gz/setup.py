import re
import subprocess

from setuptools import setup, find_packages
from setuptools.command.install import install

with open('runner1c/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        subprocess.call('runner1c sync --create --folder "{}/runner1c"'.format(self.install_libbase))


setup(
    name='runner1c',
    version=version,
    url='https://github.com/vakulenkoalex/runner1c/',
    license='BSD',
    author='Vakulenko Aleksei',
    packages=find_packages(),
    description='утилита для запуска 1С',
    python_requires='>=3.5',
    include_package_data=True,
    platforms='win32',
    entry_points={
        'console_scripts': [
            'runner1c = runner1c.core:main',
        ],
    },
    install_requires=[
        'paramiko>=2.4',
        'pytest>=3.4',
        'pytest-cov>=2.5',
        'pytest-dependency>=0.3.2'
    ],
    cmdclass={
        'install': PostInstallCommand,
    }
)
