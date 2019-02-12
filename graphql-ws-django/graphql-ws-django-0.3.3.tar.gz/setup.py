from distutils.core import setup

setup(
    name='graphql-ws-django',
    packages=['graphql-ws-django'],
    description='Websocket server for grapqh with django channels 2',
    version='0.3.3',
    author='Manviel',
    author_email='Mihaylo.Merezhko@kname.edu.ua',
    url='https://github.com/Manviel/graphql-ws',
    download_url='https://github.com/Manviel/graphql-ws',
    keywords=['graphql', 'channels'],
    install_requires=['channels', 'Django', 'graphene'],
)
