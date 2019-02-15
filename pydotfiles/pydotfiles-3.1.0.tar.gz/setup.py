from setuptools import setup, find_packages
import pydotfiles

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="pydotfiles",
    version=pydotfiles.__version__,
    author="Jason Yao",
    author_email="Hello@JasonYao.com",
    description="Fast, easy, and automatic system configuration via a configuration file/repo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JasonYao/pydotfiles",
    packages=find_packages(exclude=("bin", "build", "dist", "git", "pydotfiles.egg-info")),
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",

        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: System :: Systems Administration",

        # Supported python environments
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",

        # Supported operating systems
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",

        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    license="GPLv3",

    project_urls={
        'Bug Reports': 'https://github.com/JasonYao/pydotfiles/issues',
        # 'Funding': 'https://donate.pypi.org',
        # 'Say Thanks!': 'http://saythanks.io/to/example',
        'Source': 'https://github.com/JasonYao/pydotfiles',
    },

    # package_data={'core': ['resources/*.ini']},

    # Installation dependencies below
    install_requires=[
        'PyYAML>=3.13',
        'jsonschema>=2.6.0',
        'GitPython>=2.1.11',
        'progressbar2>=3.38.0',
        'dataclasses;python_version<"3.7"',
    ],

    scripts=['pydotfiles/bin/pydotfiles'],
    zip_safe=True,
    python_requires='>=3.6',
    extra_require={
        'dev': [
            # Linters
            'autopep8',

            # Tests
            'pyest',
            'pytest-pep8',
            'pytest-cov',
        ],
        'release': [
            'wheel',
            'twine'
        ]
    }

)
