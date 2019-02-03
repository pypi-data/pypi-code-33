from setuptools import setup, find_packages

setup(name='pyarks',
      version='0.1.4',
      description='A package to get wait times from amusement parks',
      url='http://github.com/joshimbriani/Pyarks',
      download_url='https://github.com/joshimbriani/Pyarks/archive/v0.1.4.tar.gz',
      author='Josh Imbriani',
      author_email='pypi@joshimbriani.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
            'requests>=2.21.0',
            'arrow>=0.11.0'
      ],
      zip_safe=False)