from setuptools import setup, find_packages
from pathlib import Path

long_description = (Path().cwd() / "README.md").read_text(encoding="utf8")

setup(
    # Meta-Data
    name="TstProj",
    version="1.0.2",
    description="Test",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/GregoryPevnev/python-package",
    # Additonal: Keywords, Classification, Bugs, etc.

    # Package-Configuration
    # Find all packages used in 'project'
    packages=find_packages("project"),
    python_requires=">=3.7",  # Version higher or equal to 3.7
    install_requires=[],  # Additoinal packages used by project indirectly

    # Including Static-Files
    include_package_data=True,  # Enables MANIFEST.IN
    # package_data=[],  # Alternative: Manually include assets
    # data_files=[],  # Used for moving files outside of project (To /etc or other location)

    # Scripts for users / developers (Non-Python)
    entry_points={
        'console_scripts': [
            'tst-help=project:help',
        ],
    }
)
