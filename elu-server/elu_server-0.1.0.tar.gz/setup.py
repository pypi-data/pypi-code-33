import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="elu_server",
    version="0.1.0",
    author="Marcel F",
    author_email="marcel.fasterding@gmx.de",
    description="This package handle the communication between smartphone app and hardware module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MaFa961/Eingebettete_Systeme_ELU_Server",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)