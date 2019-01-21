from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Aruana",
    version="1.0.0",
    author="Nheeng",
    author_email="contact@nheeng.com",
    description="Aruana is a collection of methods that can be used for simple NLP tasks and for machine learning text preprocessing.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://aruana.nheeng.com",
    license="Apache",
    packages=find_packages()
)

