from setuptools import setup, find_packages

try:
    with open('README.md') as f:
        long_description = f.read()
except:
    long_description=''

setup(
    name='PathCrypter',
    version='0.2',
    packages=find_packages(),
    license='CISCO',
    description='Application to encrypt files and folder-names',
    long_description=long_description,
    long_description_content_type='text/markdown', # This is important!
    url='https://github.com/techandtools/pathcrypter',
    author='Sven Baeck',
    install_requires = ['pyAesCrypt'],
    author_email='technologyandtooling@gmail.com',
    scripts = ['scripts/pathcrypter', 'scripts/pathcrypter.bat'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)