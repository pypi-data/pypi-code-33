import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Markdown2Html_French",
    version="0.0.2",
    author="Hugo Marques",
    author_email="play.craft@hotmail.fr",
    description="A Markdown to Html script using Markdown2 (French)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MrGogo400/site_statique",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)