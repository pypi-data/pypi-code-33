"""
Pypi Setup script
"""

from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(name='pydatadeck',
      version='0.9.4',
      description='Python SDK for Datadeck',
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3.7'
      ],
      keywords='datadeck',
      url='https://www.datadeck.com',
      author='Datadeck Dev',
      author_email='datadeck_dev@ptmind.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'flask==1.0.2',
          'pyyaml==3.13',
          'pytz==2018.9'
      ],
      include_package_data=True,
      zip_safe=False)
