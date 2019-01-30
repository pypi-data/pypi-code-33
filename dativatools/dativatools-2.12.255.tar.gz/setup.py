from setuptools import setup

with open('readme.md') as f:
    long_description = f.read()

def get_version():
    return open('version.txt', 'r').read().strip()

setup(name='dativatools',
      version=get_version(),
      description='A selection of tools for easier processing of data using Pandas and AWS',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://bitbucket.org/dativa4data/dativatools/',
      author='Dativa',
      author_email='hello@dativa.com',
      license='MIT',
      zip_safe=False,
      packages=['dativatools',
                'dativa.tools',
                'dativa.tools.pandas',
                'dativa.tools.aws',
                'dativa.tools.logging',
                'dativa.tools.db'],
      include_package_data=True,
      setup_requires=[
          'setuptools>=38.6.0',
          'wheel>=0.31.0'],
      install_requires=[
          'awsretry>=1.0.1',
          'boto3>=1.4.4',
          'chardet>=3.0.4',
          'pandas==0.23.4',
          'paramiko>=2.2.3',
          'patool>=1.12',
          'psycopg2>=2.7.3.1',
          'pexpect>=4.2.1',
          's3fs>=0.1.5',
          'pyarrow==0.10.0',
          'requests>=2.19.0',
          'blist>=1.3.6',
          'pycryptodome>=3.7.2'
      ],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Topic :: Software Development :: Libraries',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.6'],
      keywords='dativa',)
