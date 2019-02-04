from setuptools import setup


setup(
    name='sonoff-mqtt',
    version='1.0.0',
    packages=['sonoff'],
    entry_points={
        'console_scripts': [
            'sonoff-mqtt = sonoff.__main__:main',
            'sonoff-mqtt-config = sonoff.config:main',
        ]
    },
    install_requires=[
        'flask',
        'pyopenssl',
        'paho-mqtt',
        'flask-sockets',
        'ws4py',
    ],
)
