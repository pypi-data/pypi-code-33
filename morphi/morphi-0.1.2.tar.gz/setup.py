import os.path as osp
from setuptools import setup, find_packages


cdir = osp.abspath(osp.dirname(__file__))
README = open(osp.join(cdir, 'README.rst')).read()
CHANGELOG = open(osp.join(cdir, 'CHANGELOG.rst')).read()

install_requires = [
    'Babel',
    'six',
    'speaklater'
]
develop_requires = testing_requires = [
    'flake8',
    'mock',
    'pytest',
    'pytest-cov',
    'tox'
]

setup(
    name="morphi",
    version="0.1.2",
    setup_requires=['Babel'],
    description="i18n services for libraries and applications",
    long_description='\n\n'.join((README, CHANGELOG)),
    author="Level 12 Developers",
    author_email="devteam@level12.io",
    url='https://github.com/level12/morphi',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    license='BSD',
    packages=find_packages(),
    zip_safe=True,
    install_requires=install_requires,
    entry_points = """
    [distutils.commands]
    compile_catalog = babel.messages.frontend:compile_catalog
    extract_messages = babel.messages.frontend:extract_messages
    init_catalog = babel.messages.frontend:init_catalog
    update_catalog = babel.messages.frontend:update_catalog
    compile_json = morphi.messages.frontend:CompileJson
    """,
    extras_require={
        'develop': develop_requires,
        'testing': testing_requires
    },
)
