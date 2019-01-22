import os
from os import path
from setuptools import setup, find_packages
from setuptools.command.install import install

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()


def bashcomplete():
    cmd = "eval \"$(_NDOCKER_COMPLETE=source ndocker)\""
    with open(path.join(path.expanduser("~"), '.bashrc'), 'r+') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith(cmd):
                return

        f.seek(0, os.SEEK_END)
        f.write(cmd)


class Install(install):
    def run(self):
        bashcomplete()
        install.run(self)


setup(name='ndocker',
      version='1.0.7',
      description='docker network configration',
      long_description=long_description,
      url='http://github.com/codlin/ndocker',
      author='Sean Z',
      author_email='sean.z.ealous@gmail.com',
      cmdclass={'install': Install, },
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 2.7', ],
      install_requires=['Click==6.7', 'netaddr', 'pyyaml'],
      entry_points={
          'console_scripts': [
              'ndocker=ndocker.command_line:cli'], },
      packages=find_packages(exclude=['ndocker_test']),
      include_package_data=True,
      zip_safe=False)
