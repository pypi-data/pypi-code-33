import os
from setuptools import setup

setup(
    name="chester",
    version="0.3.0",
    author="Bendik Samseth",
    author_email="b.samseth@gmail.com",
    description="Chess Engine Tester - A simple interface to play chess engines against each other, including tournaments.",
    license="MIT",
    keywords="chess engine testing match tournament chester",
    url="https://www.github.com/bsamseth/python-chess-engine-tester",
    packages=["chester"],
    long_description=open(os.path.join(os.path.dirname(__file__), "README.md")).read(),
    long_description_content_type="text/markdown",
    install_requires=["python-chess>=0.25.1"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities",
    ],
)
