
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Python client for https://mammoth.io',
    'long_description': 'Visit https://mammoth.io/docs',
    'author': 'Mammoth developer',
    'author_email': 'developer@mammoth.io',
    'version': '1.0.9',
    'packages': ['MammothAnalytics'],
    'scripts': [],
    'name': 'mammoth-analytics-sdk',
    'install_requires': [
        'requests',
        'pytest',
        'names',
        'pydash'
    ]
}

setup(**config)
