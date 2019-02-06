

import setuptools
import os

import nicexcel as nl


# read the contents of local README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
        name='nicexcel',
        version=nl.__version__,
        # scripts=[],
        description="A package for writing nicely formatted Pandas dataframes "
                    "in Excel data files",
        long_description=long_description,
        long_description_content_type="text/markdown",
        # url="",
        packages=setuptools.find_packages(),
        python_requires=">=3.6.0",
        install_requires=['pandas>=0.20.0', 'openpyxl>=2.5.0'],
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Development Status :: 3 - Alpha",
        ],
)
