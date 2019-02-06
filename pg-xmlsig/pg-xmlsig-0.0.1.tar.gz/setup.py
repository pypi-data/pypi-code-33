import sys

from setuptools import find_packages, setup

install_requires = [
    'lxml<=3.8.0',
    'cryptography',
    'asn1crypto'
]

setup(
    name='pg-xmlsig',
    version='0.0.1',
    description='Python based XML signature. Based on xmlsig.',
    long_description='XML Signature created with cryptography and lxml',
    author="Jaime Bermeo",
    author_email="jaime.bermeo@pragmatic.com.co",
    url='http://github.com/Silverdoses/python-pgxmlsig',

    install_requires=install_requires,
    entry_points={},
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,

    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
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
