import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gisty",
    version="0.1.1",
    author="Patrick McEvoy",
    author_email="patrick.mcevoy@gmail.com",
    description="A cli utility for querying GitHub gists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/firegrass/gisty",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'tabulate',
        'maya',
        'colorama'
    ],
    entry_points={
        "console_scripts": ["gisty=gisty.gists:main"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
