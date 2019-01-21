import setuptools

setuptools.setup(
    name='libsparse',
    version='0.2.0',
    author='Antony B Holmes',
    author_email='antony.b.holmes@gmail.com',
    description='A library for dealing with sparse matrices like Pandas dataframes',
    url='https://github.com/antonybholmes/libsparse',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
