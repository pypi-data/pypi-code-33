import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name="simpleNDB",
    version= "0.9.4",
    author="Paul Harwood",
    author_email="runette@gmail.com",
    description="A very simple package to make Google Cloud Clients look more like appengine.api and NDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/runette/simpleNDB",
    install_requires=[
        "grpcio",
        "google-cloud-datastore",
        "google-cloud-storage",
        "Pillow",
        "attrdict"
    ],  
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
