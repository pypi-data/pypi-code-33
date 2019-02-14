import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="luparnet",
    version="0.1.1",
    author="Nick Lupariello",
    author_email="nicklupe13@gmail.com",
    description="A small basic neural network package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lupeboy2/luparnet",
    dowload_url="https://github.com/lupeboy2/luparnet/archive/v_001.tar.gz",
    install_requires=['numpy'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
