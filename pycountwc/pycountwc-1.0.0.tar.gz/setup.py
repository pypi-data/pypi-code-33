import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycountwc",
    version="1.0.0",
    author="Ahamed Musthafa",
    author_email="amrs.tech@gmail.com",
    description="A python 3.x package to count words, letters without space, and letters including space in a provided file.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amrs-tech/pycount",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)