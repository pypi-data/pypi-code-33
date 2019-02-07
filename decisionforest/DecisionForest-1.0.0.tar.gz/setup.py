import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DecisionForest",
    version="1.0.0",
    author="DecisionForest Ltd",
    author_email="admin@decisionforest.com",
    description="Python package for DecisionForest API access",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/decisionforest/decisionforest-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)