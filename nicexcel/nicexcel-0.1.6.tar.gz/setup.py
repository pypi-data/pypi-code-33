

import setuptools
import os


# read the contents of local README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
        name='nicexcel',
        version='0.1.6',
        scripts=[],
        description="A package for writing nicely formatted Pandas dataframes "
                    "in Excel data files",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="",
        packages=setuptools.find_packages(),
        python_requires=">=3.6.0",
        install_requires=['pandas', 'openpyxl>=2.0.0'],
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Development Status :: 3 - Alpha",
        ],
)
