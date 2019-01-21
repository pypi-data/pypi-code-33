import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='chronos-cli',
    version='0.2.6',
    author='Claude Léveillé',
    author_email='claude-leveille@outlook.com',
    description='A CLI tool that infers a next version number for Git repos.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/claude-leveille/chronos',
    packages=setuptools.find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'chronos=chronos.cli:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
)
