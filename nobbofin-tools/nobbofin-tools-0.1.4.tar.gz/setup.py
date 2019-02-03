from setuptools import setup

setup(
    name="nobbofin-tools",
    version="0.1.4",
    author="Enno Lohmeier",
    author_email="elo-pypi@nerdworks.de",
    packages=["nobbofin"],
    install_requires=["beancount >= 2.1", "simplejson >= 3.1"],
)
