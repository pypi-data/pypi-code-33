from setuptools import setup

setup(name='ledgerpy',
      version='0.1.0',
      description='python module for Ledger Nano S',
      url='https://github.com/zondax/ledger-py',
      author='ZondaX GmbH',
      author_email='info@zondax.ch',
      license='Apache 2.0',
      packages=['ledgerpy'],
      install_requires=['ledgerblue>=0.1.22'],
      zip_safe=False)
