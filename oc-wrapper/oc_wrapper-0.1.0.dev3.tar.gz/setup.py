import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="oc_wrapper",
    version="0.1.0-dev3",
    author="David Lukac",
    author_email="david.lukac@gmail.com",
    description="Python wrapper for OpenShift CLI (oc) command line tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/davidlukac/oc_wrapper",
    packages=setuptools.find_packages(),
    install_requires=[
        'python-dateutil',
        'pytz',
        'typing',
    ],
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
