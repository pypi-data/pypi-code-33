from setuptools import setup, find_packages

from digcommpy import __version__, __author__, __email__

with open("README.md") as rm:
    long_desc = rm.read()

#with open("requirements.txt") as req:
#    requirements = req.read().splitlines()

setup(
    name = "digcommpy",
    version = __version__,
    author = __author__,
    author_email = __email__,
    description = "Package for digitial communications functions",
    long_description=long_desc,
    license='BSD',
    url='https://gitlab.com/klb2/digcommpy',
    project_urls={
        'Documentation': "https://digcommpy.readthedocs.io/",
        'Source Code': 'https://gitlab.com/klb2/digcommpy'
        },
    packages=find_packages(),
    tests_require=['pytest', 'tox'],
    #install_requires=requirements,
    install_requires=[
        'numpy',
        'scipy',
        'scikit-learn',
        'joblib',
        'tensorflow',
        'hpelm',
        'keras',
        'pandas',
    ],
)
