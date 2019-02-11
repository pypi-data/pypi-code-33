import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jsql-django",
    version="1.0.3",
    author="JSQL Sp. z o.o.",
    author_email="office@jsql.it",
    description="JSQL backend plugin for Django app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.jsql.it",
    packages=setuptools.find_packages(),
    install_requires=["Django", "djangorestframework", "Pillow", "psycopg2", "pytz", "requests", "expiringdict"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
