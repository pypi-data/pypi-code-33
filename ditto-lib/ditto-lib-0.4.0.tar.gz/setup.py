from setuptools import setup, find_packages

setup(name = 'ditto-lib',
version = "0.4.0",
description = 'Data analysis tools',
url = 'https://github.com/hgromer/ditto',
author = 'Hernan Gelaf-Romer',
author_email = 'nanug33@gmail.com',
license = 'GNU',
packages = find_packages(),
install_requires = [
    "colorlogging", 
    "pympler",
    "sklearn", 
    "ordered-set"
    ],
zip_safe = False)