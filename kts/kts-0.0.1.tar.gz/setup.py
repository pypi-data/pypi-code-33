import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kts",
    version="0.0.1",
    author="Nikita Konodyuk",
    author_email="konodyuk@gmail.com",
    description="Competition-oriented framework for interactive feature engineering and building pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/konodyuk/kts",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "hashlib",
        "mprop",
        "pandas",
        "numpy",
        "scikit-learn",
        "scikit-optimize",
        "matplotlib",
        "dill",
        "feather-format",
        "xgboost",
        "lightgbm",
        "catboost"
    ]
)