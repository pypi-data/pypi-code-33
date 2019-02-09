import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MLStacker",
    version="0.0.1",
    author="Nicholas Law",
    author_email="nicholas_law_91@hotmail.com",
    description="A package which supports the implementation of stacking of machine learning models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nicholaslaw/ModelStacker",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy==1.14.0',
        'pandas==0.22.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)