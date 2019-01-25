from setuptools import setup
from requests_flask_adapter import __version__
setup(
    version=__version__,
    setup_requires=['pbr>=1.9', 'setuptools>=17.1'],
    pbr=True,
)