import setuptools

with open("README.md", 'r') as file:
    long_description = file.read()

setuptools.setup(
    name="gencoder",
    version="0.2.2",
    author="Rachit Bhargava",
    author_email="rachitbhargava99@gmail.com",
    description="Google Polyline Encoding Helper Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent"
    ],
    keywords="google polyline encoding",
    python_requires="~=3.5"
)
