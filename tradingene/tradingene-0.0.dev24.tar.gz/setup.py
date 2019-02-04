import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tradingene",
    version="0.0.dev24",
    author="Tradingene",
    author_email="i.burenko@tradingene.com",
    licence="MIT",
    description="Tradingene's package for algorithm backtest",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iburenko/tng",
    packages=setuptools.find_packages(),
    include_package_data=False,
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )    
)
