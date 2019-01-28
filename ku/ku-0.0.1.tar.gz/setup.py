import setuptools

with open('README.md', "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ku",
    version="0.0.1",
    author="Lefex",
    author_email="wsyxyxs@126.com",
    description="A serials of tools for iOS develper",
    long_description=long_description,
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)