from setuptools import setup, find_packages


setup(
      name='sumer',
      version='1.00',
      description='Sumer is a Python library for dealing with time (and date).',
      url='https://pypi.org/project/sumer',
      author='Idin',
      author_email='py@idin.ca',
      license='MIT',
      packages=find_packages(exclude=("jupyter_tests", ".idea", ".git")),
      install_requires=[],
      python_requires='~=3.6',
      zip_safe=False
)