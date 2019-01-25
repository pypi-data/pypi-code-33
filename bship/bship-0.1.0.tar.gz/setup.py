from setuptools import setup
import pathlib


dir = pathlib.Path(__file__).parent
README = (dir / 'README.md').read_text()


setup(
    name='bship',
    version='0.1.0',
    description='Battleships from the commandline.',
    long_description=README,
    long_description_content_type='text/markdown',
    keywords='battleships commandline game bship',
    url='https://github.com/dcreekp/bship',
    author='Tarbo Fukazawa',
    author_email='dcreekp@tarbo.jp',
    license='MIT',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        ],
    packages=['battleship'],
    include_package_data=True,
    install_requires=[],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "bship=battleship.__main__:run",
            ]
        },
)
