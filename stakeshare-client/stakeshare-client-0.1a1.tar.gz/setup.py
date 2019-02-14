from setuptools import setup

setup(name='stakeshare-client',
      version='0.1-alpha.1',
      description='StakeShare RPC client',
      url='https://github.com/mrmm/stakeshare-python',
      author='Ronittos',
      author_email='ronittos.dorittoss@gmail.com',
      license='Apache 2.0',
      packages=['stakeshare'],
      zip_safe=False,
      install_requires=[
          'requests',
      ]
)
