import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zdataclass",
    version="0.1",
    author="zuolongjun",
    author_email="zuo.longjun@zgmicro.com",
    description="Extension for dataclass",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zljun/zdataclass",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
)
