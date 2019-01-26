from setuptools import setup
import re


with open('preston_new/__init__.py') as f:
    version = re.search(r'(\d+\.\d+\.\d+)', f.read()).group(1)

setup(
    name='Preston_new',
    author='billypoke',
    author_email='billypoke_dev@gmail.com',
    version=version,
    license='MIT',
    description='EVE ESI API access tool',
    url='https://github.com/billypoke/Preston',
    platforms='any',
    packages=['preston_new'],
    keywords=['eve online', 'api', 'esi'],
    install_requires=[
        'requests>=2.18.4'
    ],
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ]
)
