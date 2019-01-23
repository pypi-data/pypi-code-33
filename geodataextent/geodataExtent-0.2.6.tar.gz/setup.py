import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geodataExtent",
    version="0.2.6",
    author="A^sHL^2",
    author_email="h_fock01@uni-muenster.de",
    description="Package for extracting the time and spatial extent of Geodata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HenFo/Geosoftware-II-AALLH/tree/master/CLI%20Tools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "gdal >= 2.3.0",
        "click >= 7.0",
        "netCDF4 >= 1.4.2",
        "pandas >= 0.23.4",
        "pygeoj >= 1.0.0",
        "pyshp >= 2.0.0",
        "xarray >= 0.11.0",
        "DateTime >= 4.3",
        "tabulate >= 0.8.2",
    ],
    entry_points = {
        'console_scripts': ['extract-extent=geodataExtent.masterExtract:main', 'extract2pycsw=geodataExtent.sendToPyCSW:main'],
    }
)