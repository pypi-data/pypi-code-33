import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ti_sensortag_wifi',
    version='0.0.1',
    packages=setuptools.find_packages(),
    url='https://github.com/valkjsaaa/ti_sensortag_wifi',
    author='Jackie Yang',
    author_email='me@jackieyang.me',
    description='Python Library for collecting data from TI CC3200 SensorTag',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
