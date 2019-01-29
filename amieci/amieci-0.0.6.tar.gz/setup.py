from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="amieci",
    version="0.0.6",
    description="The python API for amie",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.amie.ai",
    author="johannes beil",
    author_email="jb@amie.dk",
    license="private",
    packages=["amieci"],
    install_requires=["requests", "pandas"],
    zip_safe=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
    ],
)
