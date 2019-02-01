import setuptools

setuptools.setup(
    name="dislib",
    version="0.1.0",
    author="Barcelona Supercomputing Center",
    author_email="javier.alvarez@bsc.es",
    description="A distributed computing library on top of PyCOMPSs",
    url="https://github.com/bsc-wdc/dislib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 2 - Pre-Alpha",
        "Operating System :: POSIX :: Linux",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
)
