import os, sys
from setuptools import setup
sys.path.append('./aos')
from constant import ver

LONG_DESC = open('pypi_readme.rst').read()
LICENSE = open('LICENSE').read()

install_requires = [
    'pyserial',
    'esptool',
    'scons',
    'requests'
]

setup(
    name="aos-cube",
    version=ver,
    description="aos command line tool for repositories version control, publishing and updating code from remotely hosted repositories, and invoking aos own build system and export functions, among other operations",
    long_description=LONG_DESC,
    url='https://code.aliyun.com/aos/aos-cube',
    author='aos',
    author_email='aliosthings@service.aliyun.com',
    license=LICENSE,
    python_requires='>=2.7, <3',
    packages=["aos", "udc"],
    package_dir={'aos':'aos', 'udc':'udc'},
    package_data={'aos': ['.vscode/*'], 'udc': ['controller_certificate.pem', 'board/*/*']},
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'aos=aos.aos:main',
            'udc=udc.udc:main',
            'aos-cube=aos.aos:main',
        ]
    },
)
