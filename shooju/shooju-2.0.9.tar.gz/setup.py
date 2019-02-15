from setuptools import setup, find_packages
import os.path as p
import re

with open(p.join(p.dirname(__file__), 'shooju', '__init__.py')) as f:
    code = f.read()
    version = re.search('__version__\s*=\s*\'(\d+?\.\d+?\.\d+?)\'', code).group(1)


def read_description():
    with open('README.rst') as f:
        return f.read()


setup(name='shooju',
      version=version,
      description="Official Shooju Client",
      long_description=read_description(),
      keywords='data, client, shooju',
      author='Serge Aluker',
      author_email='serge@shooju.com',
      url='http://shooju.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "requests>=2.0.0", "six>=1.10.0"
      ]
      )
