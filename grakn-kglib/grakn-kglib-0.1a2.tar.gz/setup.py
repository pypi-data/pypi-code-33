from setuptools import setup
from setuptools import find_packages
from os import walk
from os.path import join


def create_init_files(directory):
    for dirName, subdirList, fileList in walk(directory):
        if "__init__.py" not in fileList:
            open(join(dirName, "__init__.py"), "w").close()

packages = find_packages()
for package in packages:
    create_init_files(package)
packages = find_packages()

setup(
    name = "grakn-kglib",
    version = "0.1a2",
    description = "A Machine Learning Library for the Grakn knowledge graph.",
    long_description = open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers = ["Programming Language :: Python :: 3", "Programming Language :: Python :: 3.6", "License :: OSI Approved :: Apache Software License", "Operating System :: OS Independent", "Intended Audience :: Developers", "Intended Audience :: Science/Research", "Topic :: Scientific/Engineering", "Topic :: Scientific/Engineering :: Information Analysis", "Topic :: Scientific/Engineering :: Artificial Intelligence", "Topic :: Software Development :: Libraries", "Topic :: Software Development :: Libraries :: Python Modules"],
    keywords = "machine learning logical reasoning knowledege graph grakn database graph knowledgebase knowledge-engineering",
    url = "https://github.com/graknlabs/kglib",
    author = "Grakn Labs",
    author_email = "community@grakn.ai",
    license = "Apache-2.0",
    packages=packages,
    install_requires=["astor==0.7.1", "decorator==4.3.0", "gast==0.2.0", "grakn==1.4.2", "grpcio==1.15.0", "h5py==2.8.0", "Keras-Applications==1.0.6", "Keras-Preprocessing==1.0.5", "Markdown==3.0.1", "networkx==2.2", "numpy==1.15.2", "protobuf==3.6.1", "scikit-learn==0.20.1", "scipy==1.1.0", "six==1.11.0", "tensorboard==1.11.0", "tensorflow==1.11.0", "tensorflow-hub==0.1.1", "termcolor==1.1.0", "Werkzeug==0.14.1", "grpcio==1.16.0", "protobuf==3.6.1", "six==1.11.0", "enum34==1.1.6", "twine==1.12.1", "requests==2.21.0"],
    zip_safe=False,
)
