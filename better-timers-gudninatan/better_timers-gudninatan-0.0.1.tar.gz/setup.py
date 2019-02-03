import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="better_timers-gudninatan",
    version="0.0.1",
    author="Guðni Natan Gunnarsson",
    author_email="author@example.com",
    description="Better timers for pygame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GudniNatan/better_timers",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)