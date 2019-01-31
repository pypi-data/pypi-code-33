from setuptools import setup, find_packages

setup(
    name='jupyterlab-zip',
    version='1.0.1',
    description='Zip and download folder contents',
    url='https://git.corp.adobe.com/adobesensei/jupyterlab-zip',
    author='SChatter',
    install_requires=[
        'tornado',
        'requests',
        'six',
        'jupyterlab<0.35',
        'notebook>=5.2,<6.0a',
        'flake8',
        'twine',
        'nodejs'
    ],
    data_files=[
        ("etc/jupyter/jupyter_notebook_config.d", [
            "config/jupyterlab-zip.json"
        ])
    ],
    packages=find_packages(),
    license='MIT',
    include_package_data=True,
)
