import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sml_metadata-that_some_guy",
    version="0.0.2",
    author="Walid Khalladi",
    author_email="walid.khalladi@hotmail.com",
    description="a python script to be imported in ball_tracking.py, \
              a script that creates some random players in json format",
    long_description=long_description,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
