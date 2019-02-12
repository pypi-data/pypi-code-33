import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="loxpy",
    version="0.1.1",
    author="largomst",
    author_email="yukater@outlook.com",
    description="A small implemetation of lox with python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/largomst/LoxPy",
    packages=["loxpy"],
    install_requires=[],
    entry_points={"console_scripts": ["loxpy = loxpy.Lox:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
