from setuptools import setup, find_packages

setup(
    name='jmorman-authenticator',
    version='0.0.19',
    description='Custom authenticator',
    author='John Morman',
    author_email='jmorman@microsoft.com',
    license='3 Clause BSD',
    packages=['customoauth'],
    install_requires=[
       'oauthenticator',
    ]
)
