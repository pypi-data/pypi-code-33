from setuptools import setup, find_packages


setup(
    name="textexploration",
    version="0.2.1",
    author="Matthijs Brouwer",
    url="https://github.com/textexploration/python",
    packages=find_packages(),
    license="Apache License 2.0",
    long_description=open("README.txt").read(),
    install_requires=[
        "requests >= 2.21.0",
        "pandas",
    ],
    classifiers=[
        "Framework :: Jupyter",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
)

