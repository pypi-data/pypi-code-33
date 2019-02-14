from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='htuneml',
      version='0.0.5',
      description='Monitor machine learning experiments',
      long_description=long_description,
      long_description_content_type="text/markdown",
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