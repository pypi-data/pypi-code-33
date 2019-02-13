from setuptools import setup

import nagini


setup(
    name=nagini.name + 'rest',
    version=nagini.__version__,
    author=nagini.__author__,
    description='A Python RESTful Web Service Framework',
    packages=['nagini'],
    # include_package_data=True,
    
    # install_requires=[
    #     'aiohttp',
    # ],
)
