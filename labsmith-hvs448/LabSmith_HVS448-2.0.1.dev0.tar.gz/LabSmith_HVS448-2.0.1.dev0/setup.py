import setuptools
#from distutils.core import setup, Extension
#from distutils import sysconfig
with open("README.txt","r") as fh:
	long_description = fh.read()
setuptools.setup(
    name = 'LabSmith_HVS448',
    version='2.0.1dev',
    description='Python support for controlling the LabSmith HVS448',
    author='LabSmith',
    author_email='ecummings@labsmith.com',
    url='http://www.labsmith.com',
    packages=setuptools.find_packages(),#['Python'],
    long_description=long_description,
    long_description_content_type = "text/markdown",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
	"Natural Language :: English",
    ],
  )