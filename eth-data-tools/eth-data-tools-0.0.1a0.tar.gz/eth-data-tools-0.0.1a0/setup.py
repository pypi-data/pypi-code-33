import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eth-data-tools",
    version="0.0.1-alpha",
    author="Blocklytics",
    author_email="hello@blocklytics.org",
    description="A Python package to help analyse Ethereum data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/blocklytics/eth-data-tools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English"
    ],
)