from setuptools import setup, find_packages

setup(
  name='gtmem',
  version='0.4',
  description='Google Takeout importer for Memair',
  long_description=open('README.rst').read(),
  url='https://github.com/memair/google-takeout-impoter',
  author='Greg Clarke',
  author_email='greg@gho.st',
  license='MIT',
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python'
  ],
  keywords='memair, quantified self, extended mind, lifelogging',
  packages=find_packages(),
  python_requires='>=3',
  install_requires=['memair', 'getl==0.2'],
  entry_points = {
    'console_scripts': ['gtmem=gtmem.command_line:main'],
  },
  package_data={
    'gtmem': [],
  }
)
