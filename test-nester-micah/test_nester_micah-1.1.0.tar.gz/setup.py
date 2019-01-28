import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(

    name="test_nester_micah",
    version="1.1.0",
    author="Vincent",
    author_email="micahkabala@outlook.com",
    description="A simple but memorable package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/micang404/StudyHeadFirstPython",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)