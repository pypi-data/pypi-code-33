import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fastprint",
    version="1.2",
    author="ThatOneCalculator (Kainoa Kanter)",
    author_email="kainoakanter@gmail.com",
    description="Make easy, long docstring prints with breaks between each line!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ThatOneCalculator/Python-Easy-Print",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)