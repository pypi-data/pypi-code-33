from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='dobby',
    version='1.3',
    packages=find_packages(),
    license='BSD 3-Clause',
    description="A tiny lambda handler generalizing framework for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/studyportals/Dobby',
    author='Addams Family',
    author_email='selima@studyportals.com'
)