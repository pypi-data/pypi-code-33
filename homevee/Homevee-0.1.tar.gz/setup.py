import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Homevee",
    version="0.1",
    author="Homevee",
    author_email="support@homevee.de",
    description="Dein neues Smarthome-System!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/homevee/homevee",
    scipts=['bin/homevee-server'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
