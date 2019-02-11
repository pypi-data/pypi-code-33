from setuptools import setup

setup(name='snipeit',
      version='0.10',
      description='Python library to access the SnipeIT API',
      url='http://github.com/jlbloomer/SnipeIT-PythonAPI',
      author='Jared Bloomer (Cox Automotive Inc.)',
      author_email='jared.bloomer@coxautoinc.com',
      license='MIT',
      packages=['snipeit'],
      install_requires=['requests','simplejson'],
      zip_safe=False)
