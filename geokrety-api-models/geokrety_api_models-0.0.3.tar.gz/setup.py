import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geokrety_api_models",
    version="0.0.3",
    author="Mathieu Alorent",
    author_email="kumy@geokrety.org",
    description="The GeoKrety API ORM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/geokrety/geokrety-api-models",
    packages=setuptools.find_packages(),
    install_requires=[
        "bleach==3.1.0",
        "characterentities==0.1.2",
        "SQLAlchemy==1.2.13",
        "mysqlclient==1.3.14",
        "bcrypt==3.1.6",
        "geopy==1.18.1",
        "requests[security]==2.21.0",
        "geokrety-api-exceptions==0.0.1",
    ],
    dependency_links=[
        "git+https://github.com/exavolt/python-phpass.git#egg=python-phpass",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
