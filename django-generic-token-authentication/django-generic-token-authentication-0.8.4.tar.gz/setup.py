import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-generic-token-authentication',
    version='0.8.4',
    packages=find_packages(),
    data_files=[('templates', ['authentication/templates/authentication/mail_verify.html',
                               'authentication/templates/authentication/mail_verify.txt',
                               'authentication/templates/authentication/mail_reset_passwd.html',
                               'authentication/templates/authentication/mail_reset_passwd.txt'])],
    include_package_data=True,
    license='MIT License',
    description='Adds expiring token authentication support.',
    long_description=README,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django',
        'djangorestframework',
        'django-generic-rest',
        'Pillow'
    ],
)
