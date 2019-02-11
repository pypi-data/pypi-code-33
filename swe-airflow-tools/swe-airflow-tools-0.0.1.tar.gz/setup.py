import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="swe-airflow-tools",
    version="0.0.1",
    author="Eduardo Luiz",
    author_email="swe@swe.com.br",
    description="Tools for Apache Airflow Application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/swe-eng-br/swe-airflow-tools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)