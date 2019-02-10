import setuptools
with open("README.md") as f:
    long_description = f.read();

setuptools.setup(
    name='csemver',
    version='0.1.0',
    platforms='any',
    description='Object orientied optimized variant of the semver package',
    author='Sebastian Tilders',
    author_email='info@informatikonline.net',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='GPL3',
    url='http://www.github.com/sebi2020/csemver',
    install_requires = ['semver'],
    py_modules = ['csemver'],
    classifiers=[
        'Programming Language :: Python :: 3',
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Version Control"
    ]
    );
