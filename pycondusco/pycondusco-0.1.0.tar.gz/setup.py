import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycondusco",
    version="0.1.0",
    author="Roland Stevenson",
    author_email="roland@rmg-services.com",
    description="pycondusco lets you run a function iteratively, passing it the rows of a dataframe or the results of a query.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ras44/pycondusco",
    packages=setuptools.find_packages(),
    classifiers=[
    ],
    install_requires=[
        "google-cloud-bigquery >= 1.0.0",
    ],
    setup_requires=[
        "pytest-runner",
    ],
    tests_require=[
        "pytest >= 4.0.0",
        "pystache >= 0.5.0",
    ],
)
