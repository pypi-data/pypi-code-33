import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stock_crawler_utils",
    version="0.0.9.9",
    author="Evgeny Basmov",
    author_email="coykto@gmail.com",
    description="Utils for stock-crawler project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Coykto/stock_crawler_utils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'lxml',
        'pika',
        'psycopg2-binary',
        'sqlalchemy',
    ],
)
