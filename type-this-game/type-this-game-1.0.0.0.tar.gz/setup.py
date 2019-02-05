import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="type-this-game",
    version="1.0.0",
    author="Laurențiu Andronache",
    author_email="laurentiu.andronache@trailung.ro",
    description="Simple game, where you win by typing the source code of the game itself.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Laurentiu-Andronache/type-this-game",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
