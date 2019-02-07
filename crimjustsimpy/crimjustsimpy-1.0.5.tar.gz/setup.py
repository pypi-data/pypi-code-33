from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='crimjustsimpy',
    version='1.0.5',
    description='Tools for criminal just simulation',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url='https://github.com/mdraughn/crimjustsimpy',
    author='Mark Draughn',
    author_email='mark@windypundit.com',
    keywords='criminal justice model simulation',
    packages=['crimjustsimpy'],
    python_requires='>=3.3',
    install_requires=['pandas','scipy','matplotlib','seaborn'],
    include_package_data=True,
    license='mit',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
