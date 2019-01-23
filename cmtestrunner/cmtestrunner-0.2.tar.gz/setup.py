from setuptools import setup

setup(name='cmtestrunner',
      version='0.2',
      description='custom test runner for API test',
      author='Tasin Nawaz',
      author_email='tasin.buet@gmail.com',
      license='CM',
      packages=['cmtestrunner'],
      install_requires=[
          'django',
          'djangorestframework'
      ],
      zip_safe=False)

