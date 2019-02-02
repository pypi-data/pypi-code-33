import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cognitive-services",
    version="0.0.1",
    author="Franklin Lindemberg Guimaraes",
    author_email="franklin.lindemberg@seedin.ai",
    description="A package that wraps many cognitive services packages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/franklin.lindemberg/cognitive-services",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'watson-developer-cloud>=1.3.2,<2',
        'google-api-python-client>=1.7.0,<2',
        'websocket-client>=0.48.0,<1',
        'requests>=2.21.0,<3'
    ],

)