from setuptools import setup

setup(name='python-gestpay',
      version='0.1.3',
      description='Gestpay WSs2s SOAP Client',
      url='https://bitbucket.org/metadonors/python-gestpay',
      author='Fabrizio Arzeni',
      author_email='fabrizio.arzeni@metadonors.it',
      license='MIT',
      packages=['pygestpay'],
      install_requires=[
          'suds-jurko',
      ],
      zip_safe=False)
