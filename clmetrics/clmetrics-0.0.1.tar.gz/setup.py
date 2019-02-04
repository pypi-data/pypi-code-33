import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="clmetrics",
    version="0.0.1",
    author="Luan Brasil",
    author_email="launbrasil@alu.ufc.br",
    description="A package for cluster evaluation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/weslleylc/metrics",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
