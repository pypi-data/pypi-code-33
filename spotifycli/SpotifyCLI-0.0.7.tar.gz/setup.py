import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SpotifyCLI",
    version="0.0.7",
    author="Ivy Jackson",
    author_email="ivyjs@hendrix.edu",
    description="This program controls Spotify!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ivyjsgit/Spotify-CLI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=['bin/SpotifyCLI'],
)
