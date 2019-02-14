import setuptools
with open("README.MD", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="base-aios",
    version="0.0.2",
    author="duke.lv",
    author_email="jian.lv@hotmail.com",
    description="base class package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
