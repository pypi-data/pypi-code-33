from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='gobgp_client',
    version='0.0.1',
    packages=['gobgp_client'],
    url='https://github.com/k01ek/gobgp_client',
    license='MIT',
    author='Nikolay Yuzefovich',
    author_email='mgk.kolek@gmail.com',
    description='Python gRPC client for GoBGP',
    long_description=long_description,
    install_requires=[
        'grpcio==1.16.0',
        'protobuf==3.6.1'
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ]
)
