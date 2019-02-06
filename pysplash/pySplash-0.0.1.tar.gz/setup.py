from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='pySplash',
    version='0.0.1',
    packages=find_packages(),
    url='https://gitlab.com/rouvenhimmelstein/pysplash',
    license='GNU General Public License v3.0',
    author='RouHim',
    author_email='rouvenhimmelstein@gmail.com',
    description="A simple wallpaper changer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['screeninfo'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ]
)
