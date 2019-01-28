import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="extractTool",
    version="0.4.6",
    author="Die Gruppe 1",
    author_email="c_bron02@uni-muenster.de",
    description="Tool for extracting spatial and temporal extent of Geodata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/carobro/Geosoftware2",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "Click==7.0",
        "db-sqlite3==0.0.1",
        "docopt==0.6.2",
        "geojson==2.4.1",
        "numpy==1.15.4",
        "pandas==0.23.4",
        "PyGeoj==1.0.0",
        "pylint==1.9.3",
        "pyshp==2.0.1",
        "pytest==3.3.2",
        "scipy==1.1.0",
        "wrapt==1.10.11",
        "xarray==0.11.0",
        "pyproj==1.9.5.1",
        "dateparser==0.7.0"
    ],
    entry_points = {
        'console_scripts': ['extract=extractTool.extractTool:main'],
    }
)
