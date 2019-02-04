import setuptools

# Deploy the package using twine:
# pip install -U pip setuptools twine
#
# 1. Build: python setup.py sdist bdist_wheel
# 2. Upload: twine upload dist/*

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mockquerpy",
    version="0.1.0",
    author="peakbreaker",
    author_email="andershurum@gmail.compile",
    description="A google bigquery client library mocker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/peakbreaker/MockQuerPy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
