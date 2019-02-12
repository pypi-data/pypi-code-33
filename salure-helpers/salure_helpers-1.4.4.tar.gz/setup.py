from setuptools import setup

setup(
    name='salure_helpers',
    version='1.4.4',
    description='Files with helpfull code, developed by Salure',
    url='https://bitbucket.org/salurebi/salure_helpers',
    author='Salure',
    author_email='bi@salure.nl',
    license='Salure License',
    packages=['salure_helpers'],
    package_data={'salure_helpers': ['templates/*', 'connectors/*']},
    install_requires=[
        'pandas',
        'mandrill',
        'psycopg2',
        'pymysql',
        'requests',
        'pysftp',
        'twine'
    ],
    zip_safe=False
)
