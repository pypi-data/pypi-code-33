from os import path
from setuptools import setup, find_packages


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_desc = f.read()

setup(name='ut2d',
      version='0.2.0',
      description='a command-line utility to convert unitx timestamp into human readable datetime',
      long_description=long_desc,
      long_description_content_type="text/markdown",
      url='https://github.com/estepona/ut2d',
      author='Binghuan Zhang',
      author_email='574953550@qq.com',
      classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities',
      ],
      keywords='timestamp datetime command-line scrap',
      packages=find_packages(),
      install_requires=['requests', 'bs4'],
      entry_points={
        'console_scripts': [
            'ut2d=ut2d.main:main',
        ],
      },
      zip_safe=True)