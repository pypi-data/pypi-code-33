from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='rawgpy',
      version='0.4',
      description='simple RAWG.io python api wrapper',
      url='',
      author='laundmo',
      author_email='laurinschmidt2001@gmail.com',
      license='GPLv3',
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=['rawgpy'],
      zip_safe=False,
          classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Operating System :: OS Independent",
      ],)
