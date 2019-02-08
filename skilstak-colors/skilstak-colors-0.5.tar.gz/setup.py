import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="skilstak-colors",
    version="0.5",
    description="Color library developed at Skilstak.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/reteps/skilstak-colors",
    author="Peter Stenger",
    author_email="peter.a.stenger@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["colors"],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "skilstak-colors=colors.__main__:main",
        ]
    },
)
