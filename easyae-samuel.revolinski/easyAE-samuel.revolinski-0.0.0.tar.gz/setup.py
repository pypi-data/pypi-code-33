import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
                 name="easyAE-samuel.revolinski",
                 version="0.0.0",
                 author="Samuel Revolinski",
                 author_email="samuel.revolinski@wsu.edu",
                 description="easy way for non-linear dimensionality increase or reduction",
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url="https://github.com/Zhiwu-Zhang-Lab/genetic_spectral_AutoEncoder",
                 packages=setuptools.find_packages(),
                 classifiers=[
                              "Programming Language :: Python :: 3",
                              "License :: OSI Approved :: MIT License",
                              "Operating System :: OS Independent",
                              ],
                 )
