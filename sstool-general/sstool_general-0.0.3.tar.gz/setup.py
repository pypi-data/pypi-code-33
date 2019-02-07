import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sstool_general",
    version="0.0.3",
    author="Iryna Lokhvytska",
    author_email="ilokh@softserveinc.com",
    description="A general code for the sstool.",
    long_description=long_description,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
