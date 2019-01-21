from setuptools import setup, find_packages

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='universal_response_mobile_api',
      version='0.1.5',
      description='Add universal response for your API',
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      keywords='api mobile response',
      url='https://bitbucket.org/anmv/universal-response-mobile-api',
      author='Damir Dautov, Alexandr Makarenko, Anton Medvedev',
      author_email='exorciste.2007@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'Django>=2.0', 'djangorestframework>=3.8'
      ],
      include_package_data=False,
      zip_safe=False)
