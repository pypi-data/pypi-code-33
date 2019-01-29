import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AlRegCode",
    version="0.0.2",
    author="M Nasrul Alawy",
    author_email="alphacsoft@gmail.com",
    description="The Small Package For Generate Increment Registration Code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://alphacsoft.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)