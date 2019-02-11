from setuptools import setup, find_packages

setup(
    name='jupyterhub-sxauthenticator',
    version='0.0.3',
    description='JupyterHub authenticator that hands out temporary accounts for everyone',
    url='https://github.com/jupyterhub/sxauthenticator',
    author='Yuan Xiao',
    author_email='yuan.tu.xiao@gmail.com',
    license='3 Clause BSD',
    packages=find_packages()
)
