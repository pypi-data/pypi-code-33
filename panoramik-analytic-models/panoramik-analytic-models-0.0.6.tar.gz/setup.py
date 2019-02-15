import setuptools

setuptools.setup(
    name="panoramik-analytic-models",
    version="0.0.6",
    author="Panoramik",
    author_email="panormaikinc@gmail.com",
    license="Proprietary",
    description="Panoramik ClickHouse analytic models",
    url="https://bitbucket.org/panoramik/analytic_models",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'infi.clickhouse_orm>=1.0.3',
    ]
)
