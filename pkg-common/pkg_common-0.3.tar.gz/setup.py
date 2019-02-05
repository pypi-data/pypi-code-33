from setuptools import setup, find_packages

setup(name='pkg_common',
      version='0.3',
      description='Package',
      author='Ivan Carlos Martello',
      author_email='ivcmartello@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'requests',
          'scrapy',
          'pymongo'
      ],
      zip_safe=False)