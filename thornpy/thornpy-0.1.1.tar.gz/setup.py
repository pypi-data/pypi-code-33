import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="thornpy",
    version="0.1.1",
    author="Ben Thornton",
    author_email="ben.thornton@mscsoftware.com",
    description="Miscellaneous Python Tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bthornton191/thornpy",
    packages=setuptools.find_packages(exclude=['test']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)