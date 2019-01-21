from setuptools import setup, find_packages

import os
import sys


VERSION = "0.0.4"


if sys.argv[-1] == "publish":
    print("Publishing django-bootstrap-navbar")

    os.system("python setup.py sdist")
    os.system("twine upload dist/django-bootstrap-navbar-{}.tar.gz".format(VERSION))
    sys.exit()


if sys.argv[-1] == "test":
    print("Running tests only on current environment.")

    os.system("black ./bootstrap_navbar")
    os.system("pytest --cov=bootstrap_navbar --cov-report=html")
    os.system("rm coverage.svg")
    os.system("coverage-badge -o coverage.svg")
    sys.exit()


with open("README.md") as f:
    readme = f.read()


setup(
    name="django-bootstrap-navbar",
    version="0.0.4",
    description="Django navbar package",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Bradley Stuart Kirton",
    author_email="bradleykirton@gmail.com",
    url="https://github.com/bradleykirton/django-bootstrap-navbar/",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["django"],
    extras_require={
        "dev": [
            "pytest",
            "pytest-mock",
            "pytest-cov",
            "pytest-sugar",
            "django-coverage-plugin",
            "pytest-django",
            "coverage-badge",
            "bumpversion",
            "black",
            "twine",
        ]
    },
    zip_safe=False,
    keywords="django",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.1",
    ],
)
