import io

from setuptools import find_packages
from setuptools import setup


def local_scheme(version):
    from pkg_resources import iter_entry_points

    # NOTE(awiddersheim): Modify default behaviour slighlty by not
    # adding any local scheme to a clean `master` branch.
    if version.branch == 'master' and not version.dirty:
        return ''

    for item in iter_entry_points(
        'setuptools_scm.local_scheme',
        'node-and-timestamp',
    ):
        return item.load()(version)


with io.open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='github-release-cicd',
    use_scm_version={
        'git_describe_command': 'git describe --dirty --tags --long --match "v[0-9]*.[!dev]"',
        'local_scheme': local_scheme,
        'write_to': 'github_release_cicd/version.py',
    },
    setup_requires=[
        'setuptools_scm>=3.2.0',
    ],
    author='Andrew Widdersheim',
    author_email='amwiddersheim@gmail.com',
    url='https://github.com/awiddersheim/github-release-cicd',
    description='Helper tools to handle GitHub releases.',
    long_description=long_description,
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'click>=7',
        'pygithub',
    ],
    extras_require={
        'dev': [
            'flake8',
            'flake8-bandit',
            'flake8-commas',
            'flake8-import-order',
            'flake8-import-single',
            'flake8-print',
            'flake8-quotes',
        ],
    },
    entry_points={
        'console_scripts': [
            'github_release_cicd=github_release_cicd.cli:main',
        ],
    },
    zip_safe=False,
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
    ],
    python_requires='!=2.*, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
)
