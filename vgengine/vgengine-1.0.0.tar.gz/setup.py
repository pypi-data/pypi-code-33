import os
from distutils.core import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "vgengine",
    version = "1.0.0",
    author = "Jake Burga",
    author_email = "jrburga@mit.edu",
    description = ("A general purpose game engine using the pygame graphics API and pymunk's physics engine."),
    license = "MIT",
    keywords = "game engine",
    url = "https://github.com/jrburga/VGEngine",
    packages=['cbd', 'vgengine', 'vgengine.systems', ],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent"
    ],
)