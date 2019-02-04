import setuptools

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rethinkdbcm",
    version="0.1",
    author="Mikhail Fyodorov",
    author_email="jwvsol@yandex.com",
    description="RethinkDB context manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gwvsol/RethinkDB-context-manager",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    py_modules=['rethinkdbcm'],
    install_requires=['rethinkdb'],
    include_package_data=True,
    zip_safe=False
)
