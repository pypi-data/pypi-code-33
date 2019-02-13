import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hls-edit-file",
    version="0.0.1",
    author="Rodgers Nguyen",
    author_email="cptrodgers@gmail.com",
    description="Package support cut, merge, insert hls video into hls video (m3u8)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cptrodgers/hls-edit-file",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
