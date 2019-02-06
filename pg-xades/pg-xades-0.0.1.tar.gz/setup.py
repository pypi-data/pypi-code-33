import sys

from setuptools import find_packages, setup

install_requires = [
    'pytz',
    'pg-xmlsig'
]

setup(
    name='pg-xades',
    version='0.0.1',
    description='XaDES XML signature. Based on python-xades.',
    long_description='XaDES XML Signature created with cryptography and lxml',
    author="Jaime Bermeo",
    author_email="jaime.bermeo@pragmatic.com.co",
    url='https://github.com/Silverdoses/python-pgxades',

    install_requires=install_requires,
    entry_points={},
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,

    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    zip_safe=False,
)
