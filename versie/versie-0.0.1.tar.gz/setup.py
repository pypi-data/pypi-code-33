from setuptools import find_packages, setup

docs_require = ["sphinx>=1.4.0"]

tests_require = [
    "coverage==4.5.1",
    "pytest==3.0.5",
    "requests-mock==1.4.0",
    # Linting
    "isort==4.2.5",
    "flake8==3.0.3",
    "flake8-blind-except==0.1.1",
    "flake8-debugger==1.4.0",
]

setup(
    name="versie",
    version="0.0.1",
    description="Client for the versie project",
    long_description=open("README.rst", "r").read(),
    url="https://github.com/labd/versicator-client",
    author="Lab Digital",
    author_email="opensource@labdigital.nl",
    install_requires=["requests>=2.18.4"],
    tests_require=tests_require,
    extras_require={"docs": docs_require, "test": tests_require},
    use_scm_version=True,
    entry_points={
        "console_scripts": [
            "versie=versie.cli:main",
        ],
    },
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 1.7",
        "Framework :: Django :: 1.8",
        "Framework :: Django :: 1.9",
        "Framework :: Django :: 1.10",
        "Framework :: Django :: 1.11",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    zip_safe=False,
)
