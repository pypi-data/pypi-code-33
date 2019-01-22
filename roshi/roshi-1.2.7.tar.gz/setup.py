from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="roshi",
    version="1.2.7",
    author="Abinav Bukkaraya",
    author_email="abinavbukkaraya@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bukkaraya/Roshi",
    license="MIT",
    packages=find_packages()
)
