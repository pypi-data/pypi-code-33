# encoding: utf-8
import os
import sys

from setuptools import setup, find_packages, findall


HERE = os.path.abspath(os.path.dirname(__file__))


def find_package_data():
    ignore_ext = {'.py', '.pyc', '.pyo'}
    base_package = 'cykooz'
    package_data = {}
    root = os.path.join(HERE, base_package)
    for path in findall(root):
        if path.endswith('~'):
            continue
        ext = os.path.splitext(path)[1]
        if ext in ignore_ext:
            continue

        # Find package name
        package_path = os.path.dirname(path)
        while package_path != root:
            if os.path.isfile(os.path.join(package_path, '__init__.py')):
                break
            package_path = os.path.dirname(package_path)
        package_name = package_path[len(HERE) + 1:].replace(os.path.sep, '.')

        globs = package_data.setdefault(package_name, set())
        data_path = path[len(package_path) + 1:]
        data_glob = os.path.join(os.path.dirname(data_path), '*' + ext)
        globs.add(data_glob)
    for key, value in package_data.items():
        package_data[key] = list(value)
    return package_data


README = open(os.path.join(HERE, 'README.rst')).read()
CHANGES = open(os.path.join(HERE, 'CHANGES.rst')).read()


install_requires = [
    'setuptools',
    'zc.buildout',
]
if sys.version_info < (3, 3):
    install_requires.append('virtualenv')


setup(
    name='cykooz.buildout.venv',
    version='1.2.0',
    description=u'A zc.buildout extension for run buildout under virtual python environment.',
    long_description=README + '\n\n' + CHANGES,
    keywords='development build',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Buildout',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    author='Kirill Kuzminykh',
    author_email='saikuz@mail.ru',
    license='ZPL 2.1',
    url='https://bitbucket.org/cykooz/cykooz.buildout.venv',
    package_dir={'': '.'},
    packages=find_packages(),
    namespace_packages=['cykooz', 'cykooz.buildout'],
    package_data=find_package_data(),
    zip_safe=False,
    extras_require={
        'test': [
            'pytest',
            'zc.buildout [test]'
        ],
    },
    install_requires=install_requires,
    entry_points={
        'zc.buildout.extension':
        [
            'default = cykooz.buildout.venv.extension:extension',
        ],
        'console_scripts': [
            'runtests = cykooz.buildout.venv.runtests:runtests [test]',
        ]
    },
)
