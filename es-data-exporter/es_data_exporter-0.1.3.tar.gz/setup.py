from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="es_data_exporter",
    version="0.1.3",
    author="kasen",
    author_email="kasen@outlook.com",
    description=("Elasticsearch data exporter to the Prometheus ."),
    long_description=(
        "See https://github.com/yaule/es_data_exporter/blob/master/README.md for documentation."
    ),
    license="MIT",
    keywords="prometheus exporter network monitoring elastic search",
    url="https://github.com/yaule/es_data_exporter",
    scripts=["scripts/es_data_exporter"],
    packages=["es_data_exporter"],
    install_requires=[
        "pyyaml>=3.13",
        "requests>=2.21.0",
        "requests-kerberos>=0.12.0",
        "pandas>=0.23.4",
    ],
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
    ],
)
