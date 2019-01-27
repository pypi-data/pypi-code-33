import setuptools
from setuptools import setup

setup(name='gym_pyraminx',
      version='0.0.1',
      author="Petr Tsvetkov",
      author_email="petrtsv@gmail.com",
      description="A small example package",
      long_description="...",
      long_description_content_type="text/markdown",
      url="https://github.com/pypa/sampleproject",
      packages=setuptools.find_packages(),
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      install_requires=['gym']
      )
