import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pygamemadeeasy",
    version="2019.02.11",
    author="Paul Baumgarten",
    author_email="pbaumgarten@gmail.com",
    description="A module intended to abstract away some of the complexity of using PyGame for beginner programmers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pbaumgarten.com/pygamemadeeasy",
    packages=setuptools.find_packages(),
    keywords='python pygame beginner',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['pygame'],
    python_requires='>=3'
)
