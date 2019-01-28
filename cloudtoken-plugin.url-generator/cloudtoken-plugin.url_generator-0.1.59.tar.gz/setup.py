from setuptools import setup
import os

version = os.environ['VERSION']

setup(
    name='cloudtoken-plugin.url_generator',
    version=version,
    description='URL generator plugin for cloudtoken.',
    url='https://bitbucket.org/atlassian/cloudtoken',
    author='David Ye',
    author_email='dye@atlassian.com',
    license='Apache',
    py_modules=['cloudtoken_plugin.url_generator'],
    zip_safe=False,
    python_requires='>=3.5',
    install_requires=[
        "requests>=2.20.1",
        "cloudtoken>=0.1.12",
        ],
)
