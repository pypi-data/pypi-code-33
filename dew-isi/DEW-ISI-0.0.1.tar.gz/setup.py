import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DEW-ISI",
    version="0.0.1",
    author="Genevieve Bartlett",
    author_email="bartlett@isi.edu",
    description="Distributed Experiment Workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/STEELISI/DEW",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 
