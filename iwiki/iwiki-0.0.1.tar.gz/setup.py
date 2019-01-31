
PJT_TEMA = 'wiki'

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=f"i{PJT_TEMA}",
    version="0.0.1",
    author="innovata sambong",
    author_email="iinnovata@gmail.com",
    description=f"innovata-{PJT_TEMA}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/innovata/i{PJT_TEMA}",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
