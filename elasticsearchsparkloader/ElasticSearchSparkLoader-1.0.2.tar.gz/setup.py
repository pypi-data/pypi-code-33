import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ElasticSearchSparkLoader",
    version="1.0.2",
    author="Greg Krause",
    author_email="GregCKrause@gmail.com",
    description="A module for parallel-bulk-loading a Spark Dataframe or RDD into ElasticSearch.",
    long_description="Utilizes the Python ElasticSearch module to perform a distributed, parallelized ElasticSearch bulk-load on a given Spark RDD or Dataframe.",
    long_description_content_type="text/markdown",
    url="https://github.com/GregCKrause/ElasticSearchSparkLoader",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
