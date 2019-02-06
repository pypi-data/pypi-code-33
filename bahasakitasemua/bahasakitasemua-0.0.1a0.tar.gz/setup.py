from setuptools import setup

# Package details
setup(
    name="bahasakitasemua",
    version="0.0.1a",
    entry_points={
        "console_scripts": ["bahasakita = bahasakita.cli:main"]
    },
    author="Tirtadwipa Manunggal",
    author_email="tirtadwipa.manunggal@gmail.com",
    url="https://github.com/bahasakita",
    description="Bahasa Kita Engineer Recruitment Test Repository",
    license="BSD 3-Clause License",
    packages=[
        "bahasakita",
        "bahasakita.data_engineer",
    ],
    install_requires=[
        "click==6.7",
        "colorama==0.3.9",
        "dill==0.2.7.1",
        "numpy==1.14.1"
    ],
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ]
)
