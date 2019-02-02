import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ubak",
    version="0.0.1",
    author="Unkn0wn",
    author_email="unkn0wn9@outlook.com",
    description="A simple databse backup script",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/unkn0wn9/ubak",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'cos-python-sdk-v5>=1.6.5',
    ],
    entry_points = {
        'console_scripts': ['ubak=ubak.tencent:ubak']
    },
)