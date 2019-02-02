
from setuptools import setup, find_packages
from pathlib import Path

setup(
    name = "madness",
    version = "0.4.0",
    author = "Forrest Button",
    author_email = "forrest.button@gmail.com",
    description = "wsgi microframework suitable for building modular DRY RESTful APIs",
    long_description = Path("README.md").read_text(),
    long_description_content_type = "text/markdown",
    url = "https://github.com/Waffles32/madness",
    packages = find_packages(),
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	include_package_data = False,
	install_requires = Path('requirements.txt').read_text().splitlines(),
	python_requires='>3.6',
	zip_safe = True,
)
