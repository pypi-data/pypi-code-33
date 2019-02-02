import setuptools
import diffgram.__init__ as init

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = init.__name__,
    version = init.__version__,
    author="Anthony Sarkis",
    author_email="anthonysarkis@diffgram.com",
    description="Deep learning, image annotation, training data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/diffgram/diffgram",
    packages=setuptools.find_packages(exclude=["task", "brain"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
)