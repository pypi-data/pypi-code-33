import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="atn",
    version="0.0.2",
    author="Greg Operto",
    author_email="goperto@barcelonabeta.org",
    description="A/T/N staging for Alzheimer's Disease based on CSF biomarkers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/xgrg/atn/-/archive/0.0.2/atn-0.0.2.tar.gz",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
