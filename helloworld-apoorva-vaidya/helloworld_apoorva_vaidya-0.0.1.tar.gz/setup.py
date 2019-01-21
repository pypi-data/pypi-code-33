from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='helloworld_apoorva_vaidya',
    version='0.0.1',
    description='Say Hello!',
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["helloworld"],
    package_dir={'': 'src'}
)     
