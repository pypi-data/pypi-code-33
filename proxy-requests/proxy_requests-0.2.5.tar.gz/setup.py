import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="proxy_requests",
    version="0.2.5",
    author="James Loye Colley",
    description="A wrapper for the Python 3 requests module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rootVIII/proxy_requests",
    install_requires=["requests"],
    packages = setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
