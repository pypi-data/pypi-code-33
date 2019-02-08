import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="whoisxmlapiaa",
    version="1.0.1",
    author="Vojtech Zamecnik",
    author_email="vojta.zamecnik@seznam.cz",
    description="App that print info about website from whoisxmlapi.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=["whois"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)