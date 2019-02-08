from setuptools import setup
import os

version = os.environ['VERSION']

setup(
    name='cloudtoken-plugin.google-aws',
    version=version,
    description='Google AWS plugin for cloudtoken.',
    url='https://bitbucket.org/atlassian/cloudtoken',
    author='Atlassian Cloud Engineering',
    author_email='cloud-team@atlassian.com',
    license='Apache',
    py_modules=['cloudtoken_plugin.google_aws', 'cloudtoken_plugin.google_auth'],
    zip_safe=False,
    python_requires='>=3.5',
    install_requires=[
        "cloudtoken>=0.1.12",
        "python-u2flib-host",
        "beautifulsoup4",
        "boto3",
        "Pillow",
        "requests",
        "six"
        ],
)
