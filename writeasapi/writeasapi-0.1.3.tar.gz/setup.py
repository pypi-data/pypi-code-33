from setuptools import setup

setup(
    name='writeasapi',
    version='0.1.3',
    author="CJ Eller",
    author_email="cjeller1592@gmail.com",
    description="An API client library for Write.as",
    license="MIT",
    py_modules=["writeas", "uri"],
    install_requires=["requests"],
    url="https://github.com/cjeller1592/Writeas-API",
 )
