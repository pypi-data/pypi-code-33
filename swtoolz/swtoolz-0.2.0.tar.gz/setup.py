import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="swtoolz",
    version="0.2.0",
    author="Kirill Belyaev",
    author_email="bandoftoys@gmail.com",
    description="SWToolz-Core API wrapper.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MXMP/swtoolz-api-wrapper",
    packages=setuptools.find_packages(),
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Telecommunications Industry",
        "Natural Language :: Russian",
    ],
)
