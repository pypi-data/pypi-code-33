import setuptools

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name="aircraft_carrier",
    version="0.0.1",
    author="fyb",
    author_email="fybmain@gmail.com",
    description="Booster for Web Project Carriers in Universities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url = "https://github.com/fybmain/AircraftCarrier",
    packages=["aircraft_carrier"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

