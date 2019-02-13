from setuptools import setup, find_packages
import os


ROOT = os.path.abspath(os.path.dirname(__file__))
VERSION = '1.0.2'


def get_requirements(filename):
    return open(os.path.join(ROOT, filename)).read().splitlines()


setup(
    name='ssubob',
    packages=find_packages(),
    include_package_data=True,
    install_requires=get_requirements('requirements.txt'),
    tests_require=get_requirements('test-requirements.txt'),
    version=VERSION,
    description='Soongsil Univ Food Parser',
    long_description=open(os.path.join(ROOT, 'README.md')).read(),
    long_description_content_type='text/markdown',
    author='oh inkyu',
    author_email='gomjellie@gmail.com',
    url='https://github.com/gomjellie/ssubob',
    download_url='https://pypi.python.org/pypi/ssubob',
    license='MIT LICENSE',
    platforms="Posix; MacOS X; Windows",
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development :: Testing',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    zip_safe=False,
)
