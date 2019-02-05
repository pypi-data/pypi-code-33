import setuptools
with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='WIMLib',
    version='2.0.0',
    packages=setuptools.find_packages(),
    description='WIMLib is a custom reusable libraries and objects for logging, and other operations, this version is confied to basin functions others to come',
    long_description=long_description,
    long_description_content_type="text/markdown",
	license='Public Domain',
    url='https://github.com/USGS-WiM/WIMLib',
    author='Jeremy K. Newson Web Informatics and Mapping',
    author_email='jknewson@usgs.gov',
    install_requires=[
          'requests',
          'certifi'
      ]
     #dependency_links=['http://github.com/user/repo/tarball/master#egg=package-1.0']
    )



