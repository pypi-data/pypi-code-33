from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(name="pymusician27",
      version="0.0.3-b",
      description="A python package for music composition and analysis.",
      long_description="""
      Read the README here:
      https://github.com/ScottMorse/PyMusician27
      This is the PyMusician package ported to Python 2.7
      """,
      url="https://github.com/ScottMorse/PyMusicia27",
      author="Scott Morse",
      author_email="scottmorsedev@gmail.com",
      license="Apache",
      packages=["pymusician27","pymusician27._modules"],
      include_package_data=True,
      install_requires=[
          'numpy',
      ],
      python_requires='>2.7',
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False
)