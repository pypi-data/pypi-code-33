import setuptools

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gdrivelab",
    version="0.1.11",
    author="Mikolaj Ostrzolek",
    author_email="mikolaj.ostrzolek@gmail.com",
    description="Don't wast time",
    long_description=long_description,
    #long_description_content_type="text/markdown",
    #url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
            'PyDrive',
            'pandas'
    ]
)
