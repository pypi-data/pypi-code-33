from setuptools import setup, find_packages
import os


version = '2.4.8'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'adminlte', 'test_adminlte.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.adminlte',
    version=version,
    description="Fanstatic packaging of AdminLTE",
    long_description=long_description,
    classifiers=[],
    keywords='fanstatic AdminLTE dashboard templates Ephraim Anierobi',
    author='Ephraim Anierobi',
    url = 'https://github.com/ephraimbuddy/js.adminlte',
    author_email='ephraimanierobi@gmail.com',
    license='BSD',
    packages=find_packages(),namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.bootstrap',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'adminlte = js.adminlte:library',
            ],
        },
    )
