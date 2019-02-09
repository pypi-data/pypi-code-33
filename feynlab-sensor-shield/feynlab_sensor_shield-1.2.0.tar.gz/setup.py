import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="feynlab_sensor_shield",
    version="1.2.0",
    author="FeynLab Technology, Inc.",
    author_email="social@feynlab.io",
    description="Python Library for FeynLab Sensor Shield",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://docs.feynlab.io/hardware/sensor-shield",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
)
