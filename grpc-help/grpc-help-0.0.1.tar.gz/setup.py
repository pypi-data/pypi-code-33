# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='grpc-help',
    version="0.0.1",
    keywords=("grpc", "python3"),
    description='python  grpc help package',
    author='caowenbin',
    author_email='cwb201314@qq.com',
    url='https://github.com/caowenbin/grpc-help',
    download_url='https://github.com/caowenbin/grpc-help',
    license='BSD',
    packages=["grpc_help"],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
       'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
       "grpcio>=1.17.1",
       "grpcio-tools==1.17.1",
       "protobuf>=3.6.1"
    ]
)
