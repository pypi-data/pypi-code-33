
import os
from distutils.command.register import register as register_orig
from distutils.command.upload import upload as upload_orig

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()



class register(register_orig):

    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')

class upload(upload_orig):

    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')

setup(
    name="miguelemosreverte",
    version="0.0.17",
    author="miguelemosreverte",
    author_email="miguelemosreverte@gmail.com",
    description="A small little package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    cmdclass={
        'register': register,
        'upload': upload,
    }
)
