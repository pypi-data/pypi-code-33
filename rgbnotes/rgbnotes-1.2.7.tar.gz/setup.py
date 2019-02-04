import os
import sys
from setuptools import setup, find_packages

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload --skip-existing dist/*')
    sys.exit()

with open("README.md", "r") as fh:
    readme = fh.read()


setup(name='rgbnotes',
      version='1.2.7',
      description='Python bindings for the RGB Notes API',
      long_description=readme,
      long_description_content_type='text/markdown',
      author='rgbnotes',
      author_email='support@rgbnotes.com',
      url='https://github.com/rgbnotes/rgb-python',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'requests >= 0.8.8',
      ])
