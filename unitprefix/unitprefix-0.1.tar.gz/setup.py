from setuptools import setup, find_packages


with open("README.md") as readme_file:
    readme = readme_file.read()

setup_requirements = ["setuptools_scm"]

setup(
    author="Nikhil Dhandre",
    author_email="nik.digitronik@live.com",
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="SI/NSI unit conversion",
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    setup_requires=setup_requirements,
    keywords="unitprefix",
    name="unitprefix",
    packages=find_packages(include=["unitprefix"]),
    url="https://gitlab.com/digitronik/unitprefix",
    version="0.1",
    license="GPLv2",
    zip_safe=False,
)
