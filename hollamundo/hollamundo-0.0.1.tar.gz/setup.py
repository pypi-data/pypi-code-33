from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='hollamundo',
    version='0.0.1',
    description='Say hello',
    py_modules=["hollamundo"],
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        #"License :: OSI Approved :: GNU Affero General Public License v3.0 only (AGPL-3.0-only)",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://https://github.com/lcleofa/hollamundo",
    author="lcleofa",
)