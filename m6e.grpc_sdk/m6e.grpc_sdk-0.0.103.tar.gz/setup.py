from distutils.core import setup

setup(
    name='m6e.grpc_sdk',
    packages=['m6e.grpc_sdk'],
    version='0.0.103',
    description='',
    author='',
    author_email='',
    include_package_data=True,
    url='https://github.com/m6e/grpc-sdk',
    download_url='',
    keywords=[],
    package_data={'m6e.grpc_sdk':['*', '*/*', '*/*/*']},
    install_requires=[
        'googleapis-common-protos',
        'grpcio-tools'
    ],
)
