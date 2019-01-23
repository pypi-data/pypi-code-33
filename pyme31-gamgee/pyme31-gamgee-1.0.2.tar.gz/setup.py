import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyme31-gamgee",
    version="1.0.2",
    author="Johannes Müller",
    author_email="mail@gamgee.de",
    description="Reads data from Digital Multimeter Metex ME-31 via serial port",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gamgee/pyme31",
    packages=setuptools.find_packages(),
    install_requires=[
      'pyserial'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)