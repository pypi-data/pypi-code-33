import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="steamleaderboards",
    version="0.0.1",
    author="Stefano Pigozzi",
    author_email="ste.pigozzi@gmail.com",
    description="A wrapper for the Steam Leaderboards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Steffo99/steamleaderboards",
    packages=setuptools.find_packages(),
    install_requires=[
        "lxml",
        "requests",
        "bs4"
    ],
    python_requires="~=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet"
    ]
)
