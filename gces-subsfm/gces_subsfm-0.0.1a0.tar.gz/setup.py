import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

requires = [
    'gces>=0.0.9a0',
]

extras_require = {
    'test': [
        'coverage==4.5.1',
        'pytest==3.8.1',
        'pytest-cov==2.6.0',
        'pytest-mock',
        'pytest-capturelog>=0.7',
    ],
    'ci': [
        'python-coveralls==2.9.1',
    ]
}

setup(
    name='gces_subsfm',
    version='0.0.1a0',
    description='GCES Subscriber Framework',
    long_description=README,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    author='Daniel Debonzi',
    author_email='debonzi@gmail.com',
    url='',
    keywords='pubsub gces google',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require=extras_require,
    install_requires=requires,
    entry_points = {
        'console_scripts': [
            'gces-subsfm = gces_subsfm:main'
        ]
    }
)
