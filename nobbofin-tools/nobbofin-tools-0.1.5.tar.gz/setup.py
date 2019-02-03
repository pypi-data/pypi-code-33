from setuptools import setup

setup(
    name="nobbofin-tools",
    version="0.1.5",
    author="Enno Lohmeier",
    author_email="elo-pypi@nerdworks.de",
    packages=["nobbofin", "nobbofin.importers", "nobbofin.downloaders"],
    install_requires=["beancount >= 2.1", "simplejson >= 3.1"],
)
