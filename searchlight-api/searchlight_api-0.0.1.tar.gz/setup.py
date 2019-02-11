from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="searchlight_api",
    version="0.0.1",
    description="A client to assist in connecting with the Conductor Searchlight API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dan Goodman",
    author_email="dgoodman@conductor.com",
    license="LICENSE",
    url="https://github.com/Conductor/searchlight-api-client-python",
    packages=find_packages(exclude=("docs", "searchlight_api.tests")),
    setup_requires=[
        "nose==1.3.7",
        "twine==1.12.1"
    ],
    install_requires=[
        "requests>=2.19.1",
        "simplejson>=3.11.1"
    ],
    zip_safe=False,
)
