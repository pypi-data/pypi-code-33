
from setuptools import setup
import readme_renderer.markdown
def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="Text-Converter",
    version="1.0.1",
    description="A Python package to Calculate Conventions",
    long_description=readme(),
    url="https://github.com/OMoF/Converter",
    author="Omar Faruk",
    author_email="omfaruk.om@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["Text_Converter"],
    include_package_data=True,
    install_requires=[],
)
