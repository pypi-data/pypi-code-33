import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="prophepy",
    version="0.0.1",
    description="Python mocks made for humans",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Einenlum/prophepy",
    author="Einenlum",
    author_email="yann.rabiller@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["prophepy"],
    package_dir={'prophepy': 'prophepy'},
    include_package_data=True,
    install_requires=[]
)
