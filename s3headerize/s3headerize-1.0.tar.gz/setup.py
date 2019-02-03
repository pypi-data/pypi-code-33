"""
"s3headerize" package setup.
"""

from setuptools import setup

with open('README.md', 'r') as stream:
    LONG_DESCRIPTION = stream.read()

setup(
    author='Cariad Eccleston',
    author_email='cariad@cariad.me',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Site Management'
    ],
    description='A Python package for setting HTTP headers on Amazon Web '
                'Services (AWS) S3 objects.',
    extras_require={
        'dev': [
            'autopep8',
            'coverage',
            'mock',
            'pylint'
        ]
    },
    install_requires=[
        'boto3',
        'pyyaml'
    ],
    name='s3headerize',
    license='MIT',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=[
        's3headerize'
    ],
    url='https://github.com/cariad/py-s3headerize',
    version='1.0')
