import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name='afb',
  version='v1.2.2',
  author='Siu-Kei Muk (David)',
  author_email='muksiukei@gmail.com',
  description='A base for abstract factory in Python',
  long_description=long_description,
  long_description_content_type="text/markdown",
  url='https://github.com/dave-msk/afb',
  packages=setuptools.find_packages(),
  download_url='https://github.com/dave-msk/broker/archive/v1.2.2.tar.gz',
  keywords=['afb', 'factory', 'abstract factory', 'config'],
  classifiers=[]
)
