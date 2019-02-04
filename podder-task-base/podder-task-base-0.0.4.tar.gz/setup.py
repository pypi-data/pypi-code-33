from setuptools import setup, find_packages

setup(
    name='podder-task-base',
    version='0.0.4',
    packages=find_packages(),
    author="podder-ai",
    url='https://github.com/podder-ai/podder-task-base',
    include_package_data=True,
    install_requires=[
        'grpcio-tools',
        'googleapis-common-protos',
        'python-daemon',
        'mysqlclient',
        'SQLAlchemy',
    ],
)
