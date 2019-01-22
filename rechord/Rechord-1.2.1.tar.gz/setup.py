from setuptools import setup, find_packages
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    author="Zach Davis",
    author_email="zfdavis21@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    description="A simple python script to generate chord charts.",
    entry_points='''
        [console_scripts]
        rechord=rechord.cli:cli
    ''',
    install_requires=["Click"],
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="Rechord",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/zfdavis/rechord",
    version="1.2.1",
)
