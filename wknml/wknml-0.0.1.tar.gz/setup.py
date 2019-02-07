from setuptools import setup, find_packages

setup(
    name="wknml",
    packages=find_packages(exclude=("tests",)),
    version="0.0.1",
    description="An NML library webKnossos",
    author="Norman Rzepka",
    author_email="norman.rzepka@scalableminds.com",
    url="https://scalableminds.com",
)

