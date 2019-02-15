import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="rheos_common",
    version="0.0.7",
    author="Sergei Yakneen",
    author_email="llevar@gmail.com",
    description="Classes common to various Rheos tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/llevar/rheos",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'sortedcontainers>=2.1.0'
    ]
)
