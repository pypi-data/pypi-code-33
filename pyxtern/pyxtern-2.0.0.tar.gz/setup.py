import setuptools
import os

with open("README.rst", "r") as f:
    long_description = f.read()

if not os.environ.get("CI_JOB_ID"):
    version = "2.0.0"
else:
    version = os.environ["CI_JOB_ID"]

setuptools.setup(
    name="pyxtern",
    version=version,
    author="Martin Grignard",
    author_email="mar.grignard@gmail.com",
    description="A small package to run external command lines.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://gitlab.com/mar.grignard/pyxtern",
    packages=setuptools.find_packages()
)
