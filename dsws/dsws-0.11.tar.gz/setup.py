from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='dsws',
      version='0.11',
      description='Data Science Work Space for CDSW',
      url='https://github.com/babarka/dsws',
      author='Brad Barker',
      author_email='brad@ratiocinate.com',
      license='MIT',
      packages=['dsws'],
      install_requires=[
          'thrift==0.9.3',
          'impyla>=0.14.0',
          'sasl>=0.2.1',
          'thrift_sasl==0.2.1',
          'impyla'],
      zip_safe=False)
