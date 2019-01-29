from os import path

from setuptools import setup

__version__ = '0.0.0'
project_name = 'pywinrm2'

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name=project_name,
    version=__version__,
    description='Python library for Windows Remote Management',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='winrm ws-man devops ws-management'.split(' '),
    author='Alexey Diyan',
    author_email='alexey.diyan@gmail.com',
    maintainer='Thomas Grainger',
    maintainer_email='pywinrm@graingert.co.uk',
    url='http://github.com/diyan/pywinrm/',
    license='MIT license',
    packages=('winrm', 'winrm.tests'),
    package_data={'winrm.tests': ['*.ps1']},
    install_requires=['xmltodict', 'requests>=2.9.1', 'requests_ntlm>=0.3.0', 'six'],
    extras_require = dict(kerberos=['requests-kerberos>=0.10.0'], credssp=['requests-credssp>=0.0.1']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Clustering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration'
    ],
)
