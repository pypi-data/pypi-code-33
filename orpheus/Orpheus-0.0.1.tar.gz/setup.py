import setuptools

long_description = '''
This is an intelligence music retrieval engine
that takes in short musical phrases as a search
query and returns a best match from our database.
The intent is to let users discover the songs that
have forever been stuck in their heads whose names
elude them.

This package uses Python 3.6 and support is not 
guaranteed for other versions.
'''
setuptools.setup(
    name="Orpheus",
    version="0.0.1",
    author="Harish Kumar",
    author_email="harishk1908@gmail.com",
    description="An intelligent music retrieval engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)
