from setuptools import setup, find_packages


setup(
      name='chronology',
      version='1.01',
      description='Chronology is a Python library for dealing with time (and date).',
      url='https://github.com/idin/chronology',
      author='Idin',
      author_email='py@idin.ca',
      license='MIT',
      packages=find_packages(exclude=("jupyter_tests", ".idea", ".git")),
      install_requires=[],
      python_requires='~=3.6',
      zip_safe=False
)