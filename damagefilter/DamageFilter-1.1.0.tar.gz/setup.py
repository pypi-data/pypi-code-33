#!/usr/bin/env python
from setuptools import setup

setup(
    name = "DamageFilter",
    version = "1.1.0",
    packages = ["DamageFilter"],
    package_dir = {"DamageFilter":"src"},
    install_requires = ["pysam","pyvcf","scipy"],
    author="Yong Deng",
    author_email = ["dengyong@geneplus.org.cn","yodeng@tju.edu.cn"],
    description = "For Artifact DNA damage filter",
    license="MIT",
    entry_points = {
        'console_scripts': [  
            'DamageFilter = DamageFilter.DamageFilter:main'
        ]
    }

)

