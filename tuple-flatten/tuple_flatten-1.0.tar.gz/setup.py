import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tuple_flatten",
    version="1.0",
    author="El Sholz",
    author_email="fewav@braun4email.com",
    description="Basically only a function to iterate through tuples and add their values. Example: (1,2)+(2,3)=(3,5)",
    long_description=long_description,
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
)

class a():
    def __init__(self, hello: int):
        pass