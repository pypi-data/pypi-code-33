from setuptools import setup

setup(name='python-checkit',
      version='0.1.3',
      description='Checkit API Client',
      url='https://bitbucket.org/metadonors/python-checkit',
      author='Metadonors',
      author_email='fabrizio.arzeni@metadonors.it',
      license='MIT',
      packages=['pycheckit'],
      install_requires=[
          'requests',
      ],
      extras_require={
        'dev': [
            'pytest',
            'pytest-pep8',
            'pytest-cov'
        ]
      },
      zip_safe=False)