from setuptools import setup, find_packages

setup(
    name='browsercam',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask'
    ],
    long_description=open('README.md').read()
)
