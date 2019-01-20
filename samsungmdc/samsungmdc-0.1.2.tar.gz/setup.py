import setuptools


setuptools.setup(
    name="samsungmdc",
    version="0.1.2",
    description="Implementation of the Multiple Display Control Protocol.",
    url="https://git.vpgrp.io/noc/python-mdc",
    author="Damien PLENARD",
    author_email="dplenard@vente-privee.com",
    license="Apache License 2.0",
    long_description="""Implementation of the Samsung Multiple Display Control
    Protocol through Ethernet/Wireless. Right now, this implementation is
    tested only on Samsung DM-E Series and specifically on the Samsung
    LH55DMEPLGC/EN.""",
    entry_points={
        "console_scripts": ["mdc=mdc.__main__:main"]
    },
    packages=["mdc"],
    test_suite="tests",
    install_requires=[],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Home Automation",
        "Topic :: Multimedia :: Video :: Display"
    ],
)
