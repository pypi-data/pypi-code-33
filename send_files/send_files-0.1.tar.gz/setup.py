from distutils.core import setup
from setuptools import find_packages

setup(name='send_files',
      author='Fischers Fritz',
      author_email='fischersfritz@sent.at',
      description='Copy files between computers.',
      url='https://fritz.ftp.sh/fossil/send_files',
      packages=find_packages('.'),
      install_requires=[
          'horetu[wsgi]>=0.4.3',
      ],
      classifiers=[
          'Programming Language :: Python :: 3.6',
      ],
      version='0.1',
      license='AGPL',
      )

