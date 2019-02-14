from setuptools import setup, find_packages

setup(
    name='browsercam',
    version='0.1',
    packages=find_packages(),
    package_data={'': ['webcam.html']},
    include_package_data=True,
    install_requires=[
        'flask'
    ],
    long_description=open('README.md').read()
)
