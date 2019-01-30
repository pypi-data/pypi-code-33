from setuptools import setup
from incenp.pebble import __version__

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
        name = 'incenp.pebble',
        version = __version__,
        description = 'Command-line Passman client',
        long_description = long_description,
        long_description_content_type = 'text/markdown',
        author = 'Damien Goutte-Gattat',
        author_email = 'dgouttegattat@incenp.org',
        url = 'https://git.incenp.org/damien/pebble',
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7'
            ],
        install_requires = [
            'requests',
            'sjcl'
            ],
        packages = [
            'incenp',
            'incenp.pebble',
            'incenp.pebble.cli'
            ],
        entry_points = {
            'console_scripts': [
                'pbl = incenp.pebble.__main__:main'
                ]
            },
        command_options = {
            'build_sphinx': {
                'project': ('setup.py', 'Pebble'),
                'version': ('setup.py', __version__),
                'release': ('setup.py', __version__)
                }
            }
        )
