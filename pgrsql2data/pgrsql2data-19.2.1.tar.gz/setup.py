from setuptools import find_packages, setup

LONG_DESCRIPTION = open("README.md").read()

INSTALL_REQUIRES = ["geomet", "fastavro"]

setup(
    name="pgrsql2data",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="Utility for converting PgRouting SQL scripts output by osm2po to data files (CSV, JSON or Avro).",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="http://github.com/christippett/pgrsql2data",
    author="Chris Tippett",
    author_email="c.tippett@gmail.com",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages("src"),
    entry_points={"console_scripts": ["pgrsql2data=pgrsql2data.cli:run"]},
    install_requires=INSTALL_REQUIRES,
    keywords="osm2po pgrouting openstreetmap",
    python_requires=">=3",
    classifiers=[
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    zip_safe=False,
)
