import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='rockstarfoxdot',    # This is the name of your PyPI-package.
    version='1.0.0',                          # Update the version number for new releases
    url="https://github.com/stretchyboy/rockstarfoxdot",
    author="Martyn Eggleton",
    author_email="martyn.eggleton@gmail.com",
    description="Using using the RockStar EsoLang to make music in FoxDot ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
