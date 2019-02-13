from setuptools import setup, find_packages

_MAJOR = 0
_MINOR = 1
_MICRO = 2

# Adding list of requirements
with open("requirements.txt", "r") as f:
    requirements = f.read().split()

with open("README.rst", "r") as f:
    readme = f.read()

setup(
    name="pynextgen",
    version=f"{_MAJOR}.{_MINOR}.{_MICRO}",
    author="Etienne Kornobis",
    author_email="ekornobis@gmail.com",
    description="[UNSTABLE] A package of custom tools to tackle bioinformatic projects.",
    long_description=readme,
    url="http://pypi.org/project/pynextgen/",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "divergent_transcription=pynextgen.scripts.divergent_transcription:main"
        ]
    },
    classifiers=["Programming Language :: Python :: 3"],
)
