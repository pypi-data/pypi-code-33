from setuptools import setup

setup(name='PyAcryl',
      version='0.1.6',
      description='Object-oriented library for the Acryl blockchain platform',
      url='https://github.com/acrylplatform/PyAcryl',
      author='PyAcryl',
      author_email='dp@theinvaders.pro',
      license='MIT',
      packages=['pyacryl'],
      keywords=['acryl', 'blockchain', 'analytics', 'crypto'],
      install_requires=[
            'base58==0.2.5',
            'pyblake2==1.1.2',
            'python-axolotl-curve25519==0.4.1.post2',
            'requests==2.21.0'
      ]
      )


