from setuptools import setup

setup(
    name = 'ddls3utils',
    packages = ['ddls3utils'],
    version = '0.0.6',
    description = 'S3 utils',
    author = 'nedlitex',
    author_email = 'nedlitex0053@gmail.com',
    url = 'https://github.com/Nedlitex/s3utils',
    keywords = ['s3'],
    license='MIT',
    install_requires=['boto3'],
)