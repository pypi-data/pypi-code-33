import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="japtkpy",
    version="0.0.5",
    author="Sheharyar Naseem",
    author_email="sherryfbi1994@gmal.com",
    description="A simple Japanese Language Tokenizer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sherryt400/japtkpy",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'rakutenma==0.3.3'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)