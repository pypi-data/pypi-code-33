import os
from setuptools import find_packages, setup
import bab_project

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-bab-project',
    version=bab_project.__version__,
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',  # example license
    description='Django project pour la boite à bidules.',
    long_description=README,
    url='https://www.boite-a-bidules.com/',
    author='Nicolas Pierrot',
    author_email='info@boite-a-bidules.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
