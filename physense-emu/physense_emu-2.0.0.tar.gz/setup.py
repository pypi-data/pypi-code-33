# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='physense_emu',  # Required
    version='2.0.0',  # Required
    description='A sample Python project',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/primeteacher/physense_emu',  # Optional
    author='Jason Silverstein',  # Optional
    author_email='jsilver5@dtcc.edu',  # Optional
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

    keywords='itn160',  # Optional

    packages=find_packages(),  # Required

    install_requires=['physense_sim'],  # Optional

)
