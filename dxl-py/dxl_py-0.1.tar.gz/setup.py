import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='dxl_py',
    version='0.1',
    author='Hugo Ponte',
    license='MIT',
    description='Dynamixel SDK Python Wrapper',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/HugoCMU/dxl_py.git',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
