import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rkpython",
    version="0.0.14",
    author="Roemer Kleerebezem",
    author_email="roemer.kleerebezem@gmail.com",
    description="Python module containing various functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/roemerkleerebezem/rkpython",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)