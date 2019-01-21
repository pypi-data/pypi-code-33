from setuptools import setup, find_packages
from os import path



setup(
    name="regxtools",
    version="1.0.6",

    author="Jean M. Girard",
    author_email="Jean.M.Girard@Outlook.com",

    description="Tools for regular expressions ",
    long_description_content_type="text/markdown",
    url="https://github.com/JeanMGirard/RegxTools",
    keywords='code-listing regex development',
    packages=[
        'regxtools'
    ],
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/JeanMGirard/RegxTools/issues',
        'Funding': 'https://donate.pypi.org',
        'Source': 'https://github.com/JeanMGirard/RegxTools',
    },
    install_requires=[
    ],
    classifiers=[
        #   3 - Alpha               #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
         'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    #entry_points={  # Optional
    #    'console_scripts': [
    #        'sample=sample:main',
    #    ],
    #},
)
