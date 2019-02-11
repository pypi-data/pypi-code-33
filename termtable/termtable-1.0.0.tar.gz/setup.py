import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README.md"), 'r') as readme_file:
    setup(
        name="termtable",
        version="1.0.0",
        description="Pretty text-based interactive terminal tables",
        long_description=readme_file.read(),
        long_description_content_type="text/markdown",
        url="https://github.com/jknielse/termtable",
        author="Jacob Kerr Nielsen",
        author_email="jake.k.nielsen@gmail.com",
        license="MIT",
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 2.7",
        ],
        packages=["termtable"],
        include_package_data=True,
        install_requires=["colored"],
    )
