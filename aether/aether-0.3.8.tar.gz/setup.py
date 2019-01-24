from setuptools import setup, find_packages
import aether as ae

def _parse_requirements():
    with open('requirements_aether_user.txt') as f:
        install_requires = f.read().strip().split('\n')
        return install_requires


with open("README.md", "r") as fh:
    long_description = fh.read()

classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering :: GIS',
    'Topic :: Scientific/Engineering :: Atmospheric Science',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Scientific/Engineering :: Physics',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
]


# python setup.py sdist upload -r pypi
setup(
    name = 'aether',
    packages = find_packages(),
    install_requires=_parse_requirements(),
    version = ae.__version__,
    description = 'Welcome to the Aether Platform',
    long_description=long_description,
    author = 'David Bernat',
    author_email = 'david@starlight.ai',
    url = 'https://davidbernat.github.io/aether-user/html/index.html',
    classifiers=classifiers,
    keywords = ['satellite', 'imagery', 'remote sensing', "starlight", "platform", "gis"],
)