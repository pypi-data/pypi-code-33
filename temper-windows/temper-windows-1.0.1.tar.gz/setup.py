import setuptools
import sys

if sys.version_info.major == 3:
    # noinspection PyArgumentList
    long_description = open('README.md', encoding='utf-8').read()
else:
    # noinspection PyUnresolvedReferences
    long_description = open('README.md').read().decode("utf-8")

setuptools.setup(
    name='temper-windows',
    version='1.0.1',
    author='Tom Churchill',
    author_email='tom@tomchurchill.co.uk ',
    description='Gets the temperature from a Temper USB thermometer on windows.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/tom-churchill/temper-windows',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    install_requires=[
        'pywinusb>=0.3.2',
    ],
)