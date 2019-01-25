import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='tablextract',
    version='1.0.0',
    author='Juan C. Roldan',
    author_email='juancarlos@sevilla.es',
    description='Extract the information represented in any HTML table',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/juancroldan/tablextract',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)