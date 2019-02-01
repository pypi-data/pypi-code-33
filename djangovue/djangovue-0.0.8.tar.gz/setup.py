from setuptools import setup, find_packages

import os
import sys
import shutil


VERSION = "0.0.8"


if sys.argv[-1] == "publish":
    print("Publishing djangovue")

    os.system("python setup.py sdist")
    os.system("twine upload dist/djangovue-{}.tar.gz".format(VERSION))

    shutil.rmtree("dist")
    shutil.rmtree("djangovue.egg-info")
    sys.exit()


if sys.argv[-1] == "test":
    print("Running tests only on current environment.")

    os.system("black ./djangovue")
    os.system("pytest --cov=djangovue --cov-report=html")
    os.system("rm coverage.svg")
    os.system("coverage-badge -o coverage.svg")
    sys.exit()


with open("README.md") as f:
    readme = f.read()


setup(
    name="djangovue",
    version=VERSION,
    description="A set of helper tags and form widgets for making django and vue play nicely.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Bradley Stuart Kirton",
    author_email="bradleykirton@gmail.com",
    url="https://github.com/bradleykirton/django-vue/",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    license="MIT",
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
    keywords="djangovue",
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
