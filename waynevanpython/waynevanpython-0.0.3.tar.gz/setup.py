import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="waynevanpython",
    version="0.0.3",
    author="Wayne Van Son",
    author_email="waynevspersonal@gmail.com",
    description="An example, but mainly shortcuts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/waynevanson/waynevanpython",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)