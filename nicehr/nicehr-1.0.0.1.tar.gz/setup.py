from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='nicehr',
    version='1.0.0.1',
    packages=['nicehr'],
    url='https://github.com/dagonis/nicehr',
    author='Kevin Tyers',
    author_email='ktyers+pypi@gmail.com',
    long_description_content_type="text/markdown",
    description='Nice Autoscaling Horizontal Rules for Python',
    install_requires=['colored'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Natural Language :: English"
    ],
)