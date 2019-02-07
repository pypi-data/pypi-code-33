from setuptools import setup

setup(name='htuneml',
      version='0.0.3',
      description='Monitor machine learning experiments',
      url='http://github.com/johnsmithm/htuneml',
      author='Ion Mosnoi',
      author_email='moshnoi2000@gmail.com',
      license='MIT',
      packages=['htuneml'],
      install_requires=[
           'requests'
      ],      
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)