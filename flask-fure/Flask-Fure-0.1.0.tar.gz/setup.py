from os import path
from codecs import open
from setuptools import setup


basedir = path.abspath(path.dirname(__file__))

with open(path.join(basedir,'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
        name='Flask-Fure',
        version='0.1.0',
        url='',
        license='MIT',
        author='LIHTFS',
        author_email='xiaozekun2017@gmail.com',
        description='Create social share.',
        long_description=long_description,
        long_description_content_type='text/markdown',
        platforms='any',
        packages=['flask_fure'],
        zip_safe=False,
        test_suite='test_flask_fure',
        include_package_data=True,
        install_requires=['Flask'],
        keywords='flask extension development',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Python Modules'
            ]
        )
