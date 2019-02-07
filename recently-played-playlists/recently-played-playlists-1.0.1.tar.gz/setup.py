from setuptools import setup

setup(
    name='recently-played-playlists',
    version='1.0.1',
    description='Poll Spotify listening history and log to MySQL, & HTTP API for recently-played-playlists-parser.',
    author="@ndelnano",
    author_email="nickdelnano@gmail.com",
    url='https://github.com/ndelnano/recently-played-playlists',
    install_requires=[
        'flask',
        'mysqlclient',
        'python-dotenv',
        'ndelnano-spotipy',
    ],
    license='LICENSE.txt',
    packages=[
        'recently_played_playlists',
        'recently_played_playlists.api',
        'recently_played_playlists.cli',
        'recently_played_playlists.db',
        'recently_played_playlists.spotify',
    ],
    entry_points = {
        'console_scripts': [
            'recently-played-playlists = recently_played_playlists.cli.main:main'
        ]
    }
)
