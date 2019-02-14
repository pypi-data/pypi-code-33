from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="dim-tools",
    version="3.0.1b",
    author="Dmitry Pakalnis",
    author_email="dmitry@unipat.ru",
    description="Useful python functions, the way I see them",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dmitiris/python-dim-tools",
    packages=['dimtools', ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
