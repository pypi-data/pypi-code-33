import pypandoc

from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

# Convert the README.md to README.rst
with open('README.rst', 'w', encoding='utf-8') as readme:
    readme.write(pypandoc.convert_file('README.md', 'rst', format='markdown'))

setup(
    name='glue-setuptools',

    version='0.4',

    description='A Command extension to setuptools that allows building an AWS Glue dist and uploading to S3',
    long_description=pypandoc.convert_file('README.md', 'rst', format='markdown'),

    url='https://github.com/x3n1x/glue-setuptools',

    author='Lionel Molinier',
    author_email='lionel@molinier.eu',

    license='APL 2.0',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.7',
        ],

    keywords='setuptools extension',

    install_requires=['boto3', 'setuptools', 'wheel', 'pypandoc'],

    package_dir={'': '.'},
    packages=find_packages('.'),

    setup_requires=['pypandoc'],

    entry_points={
        'distutils.commands': [
            'gdist = glue_setuptools.gdist:GDist',
            'gupload = glue_setuptools.gupload:GUpload',
        ],
        'distutils.setup_keywords': [
            'glue_entrypoint = glue_setuptools.gdist:validate_glue_entrypoint',
        ],
    }
)