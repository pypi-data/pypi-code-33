import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

def consume(target):
    files = []
    for root, _, filelist in os.walk(target):
        files = [os.path.join(root, file) for file in filelist]
        files.extend(files)
    return files

setuptools.setup(
    name="bazeler",
    version="0.0.5",
    author="Ian Baldwin",
    author_email="ian@iabaldwin.com",
    description="Bazel helper package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PointOneNav/bazeler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        'console_scripts': ['bazeler=bazeler.command_line:main'],
    },
    include_package_data = True,
    install_requires = ['jinja2', 'colorama'],
)
