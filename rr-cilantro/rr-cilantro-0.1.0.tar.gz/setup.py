from setuptools import setup

VERSION = "0.1.0"

setup(
    name='rr-cilantro',
    version=VERSION,
    url='https://github.com/RedRiverSoftware/cilantro/',
    author='Red River Software',
    author_email='os@river.red',
    description='A CamJam Edukit 3 Wrapper',
    long_description=open('README.md').read(),
    packages=['cilantro'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    python_requires='>=3.4',
    keywords=['cilantro', 'robot', 'camjam'],
    install_requires=[
        'gpiozero==1.4.1',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
