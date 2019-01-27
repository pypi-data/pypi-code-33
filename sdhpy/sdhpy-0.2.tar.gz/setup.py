from setuptools import setup, find_packages

setup(name='sdhpy',
      version='0.2',
      description='The SDH Python Data Connector',
      url='http://www.smartdatahub.io',
      author='Smart Data Hub',
      author_email='sales@smartdatahub.io',
      license='SDH',
      packages=find_packages(),
      install_requires=['requests','pandas', 'ckanapi'],
      zip_safe=False)