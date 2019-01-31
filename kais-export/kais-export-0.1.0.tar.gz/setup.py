from setuptools import setup, find_packages


setup(
    name='kais-export',
    version='0.1.0',
    packages=find_packages(),
    url='https://github.com/gisce/kais-export',
    license='GPLv2',
    install_requires=['django-copybook'],
    author='GISCE-TI, S.L.',
    author_email='devel@gisce.net',
    description='Export account moves to KAIS',
)
