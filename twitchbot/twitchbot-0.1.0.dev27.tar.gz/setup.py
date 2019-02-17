import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='twitchbot',
    version='0.1.0.dev.27',
    author='Qlii256',
    author_email='me@rubenportier.be',
    description='A bot for twitch streamers making use of Twitch IRC and Twitch API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Qlii256/twitchbot',
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=['aiohttp', 'multidict', 'python-dateutil'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
)
