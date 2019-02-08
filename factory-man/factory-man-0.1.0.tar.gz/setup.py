import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="factory-man",
    version="0.1.0",
    author="Eerik Sven Puudist",
    author_email="eerik@herbfoods.eu",
    description="Extensions for Factory Boy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/eeriksp/factory-man",
    packages=setuptools.find_packages(),
    install_requires=[
        'factory_boy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)