import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

def get_version():
	with open("version.txt","r") as f:
		return f.read()
	

setuptools.setup(
    name="jivi",
    version=get_version(),
    author="Joris Vercleyen",
    author_email="jorisvercleyen@gmail.com",
    description="Joris Vercleyen his personal library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)