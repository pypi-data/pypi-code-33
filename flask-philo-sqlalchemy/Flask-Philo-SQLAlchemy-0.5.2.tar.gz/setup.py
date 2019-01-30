from setuptools import setup


long_version = """
Flask-Philo extension that provides Integration with SQLAlchemy
"""


setup(
    name='Flask-Philo-SQLAlchemy',
    version='0.5.2',
    description='Flask-Philo plugin that provides support for SQLAlchemy',
    long_description='',
    packages=[
        'flask_philo_sqlalchemy'

    ],
    url='https://github.com/Riffstation/Flask-Philo-SQLAlchemy',
    author='Manuel Ignacio Franco Galeano',
    author_email='maigfrga@gmail.com',
    license='Apache',
    install_requires=[
        'sqlalchemy',
        'bcrypt',
        'Flask-Philo-Core',
        'jsonschema==2.6.0',
        'webcolors==1.8.1',
        'pytest==4.0.0'

    ],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Framework :: Flask',
        'Programming Language :: Python :: 3',
    ],
    keywords='flask REST framework',
    entry_points={
        "console_scripts": [
        ]
    }
)
