from setuptools import setup, find_packages
import os
import shutil

try:
    with open('README.md') as f:
        long_description = f.read()
except:
    long_description = ''

try:
    platform_files_path = os.path.join(os.path.dirname(__file__), "platform_files")
    osx_path = os.path.join(platform_files_path, "osx_workflows")
    static_data_path = os.path.join(platform_files_path, "..", "pathcrypter", "static_data")
except:
    pass

if os.path.exists(static_data_path):
    shutil.make_archive(os.path.join(static_data_path, "osx_workflows"), 'zip', osx_path)
setup(
    name='PathCrypter',
    version='0.5',
    packages=find_packages(),
    license='CISCO',
    description='Application to encrypt files and folder-names',
    long_description=long_description,
    long_description_content_type='text/markdown',  # This is important!
    url='https://github.com/techandtools/pathcrypter',
    author='Sven Baeck',
    install_requires=['pyAesCrypt', 'pycrypto>=2.6.1'],
    author_email='technologyandtooling@gmail.com',
    scripts=['scripts/pathcrypter',
             'scripts/pathcrypter.bat'],
    package_data={
        'pathcrypter.static_data' : [ '*.zip' ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
