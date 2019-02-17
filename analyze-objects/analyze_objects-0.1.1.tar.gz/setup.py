import setuptools


with open("README.rst", "r") as f:
    long_description = f.read()


setuptools.setup(
    name="analyze_objects",
    version="0.1.1",
    author="Philip Schill",
    author_email="philip.schill@gmx.de",
    url="https://gitlab.com/pschill/analyze_objects",
    description="Contains command line tools an python functions to search symbols in object files (.o, .obj).",
    long_description=long_description,
    python_requires=">=3.6",
    packages=["analyze_objects"],
    entry_points={
        "console_scripts": [
            "find_symbols = analyze_objects.find_symbols:main"
        ]
    },
    install_requires=[
        "colorama"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development",
        "Topic :: Utilities"
    ]
)
