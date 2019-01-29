import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="smalldata",
    version="0.0.2",
    author="Martin Virtel",
    author_email="martin.virtel@gmail.com",
    description="Unix Pipe Fittings For Data Science",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mvtango/smalldata",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points = {

        'console_scripts' : [

                             'sd_c=smalldata.counter:main',
                             'sd_g=smalldata.groupby:main',
                             'sd_e=smalldata.extract:main',

                            ]

    }
)
