import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()



setuptools.setup(
    name="wyspypi001",
    version="0.0.2",
    author="wys",
    author_email="author@example.com",
    description="wys first pypi",
    long_description= 'long desc',
    long_description_content_type="text/markdown",
    url="http://www.ym18.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)