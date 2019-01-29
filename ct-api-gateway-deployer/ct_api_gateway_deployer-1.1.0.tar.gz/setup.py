import os

from setuptools import setup, find_packages

_here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r") as fh:
    long_description = fh.read()

version = {}
with open(os.path.join(_here, 'ct_api_gateway_deployer', 'version.py')) as f:
    exec(f.read(), version)

package_requirements = [
    'boto3>=1.9',
    'Flask>=1.0',
    'Flask-RESTful>=0.3',
    'jsonschema>=2.6',
    'ruamel.yaml>=0.15'
]

setup(
    name="ct_api_gateway_deployer",
    version=version['__version__'],
    author="Cinnecta",
    author_email="cinnecta.dev@gmail.com",
    description="Package to automatize the configuration of an Flask API REST application inside the AWS API Gateway.",
    long_description=long_description,
    long_description_content_type="text/plain",
    url="https://bitbucket.org/cinnecta/ct-api-gateway-deployer.git",
    packages=find_packages(),
    include_package_data=True,
    install_requires=package_requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)