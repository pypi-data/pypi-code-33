import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='rossby',
    version='0.0.2',
    author='Nicholas Tulli',
    author_email='nat5142@psu.edu',
    description='A wrapper for the U.S. National Weather Service API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nat5142/rossby',
    python_requires='>=3.6',
    packages=setuptools.find_packages(exclude='tests'),
    install_requires=['requests>=2.20', 'addict==2.2.0'],
    keywords='national weather service nws noaa api wrapper',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]
)
