"""
setup.py file for temperature module
"""

from setuptools import setup, find_packages
from distutils.core import setup, Extension

temperature_module = Extension('_temperature', sources=['temperature/temp_wrap.cxx'], library_dirs=['lib'],
                               libraries=['Temperature'])

setup(name='temperature',
      version='0.5',
      author="SF Zhou WingC",
      author_email="1018957763@qq.com",
      url="https://gitlab.com/KD-Group/temperature",

      license='GPL',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',

          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Programming Language :: Python :: 3',
      ],

      description="Python module for temperature",
      ext_modules=[temperature_module],
      packages=find_packages(),
      data_files=[('', ['lib/Temperature.dll'])],
      python_requires='>=3',
      )
