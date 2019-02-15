from setuptools import setup

version = "0.7"
long_description = "\n\n".join([open("README.rst").read(), open("CHANGES.rst").read()])
install_requires = ["requests"]
tests_require = ["pytest", "mock", "pytest-cov", "pytest-flakes", "pytest-black"]
setup(
    name="threedi-scenario-downloader",
    version=version,
    description="Tools for downloading results for 3Di scenarios",
    long_description=long_description,
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=["Programming Language :: Python", "Framework :: Django"],
    keywords=[],
    author="Emiel Verstegen",
    author_email="emiel.verstegen@nelen-schuurmans.nl",
    url="https://github.com/nens/threedi-scenario-downloader",
    license="MIT",
    packages=["threedi_scenario_downloader"],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={"test": tests_require},
)
