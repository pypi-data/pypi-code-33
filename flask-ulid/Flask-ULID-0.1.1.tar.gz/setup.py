from setuptools import setup


setup(
    name='Flask-ULID',
    version='0.1.1',
    url='https://github.com/setomits/flask-ulid/',
    license='MIT',
    author='Mitsuhiro Setoguchi',
    author_email='setomits@gmail.com',
    description='URL conveter with ULID on Flask',
    py_modules=['flask_ulid'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'ulid-py'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
